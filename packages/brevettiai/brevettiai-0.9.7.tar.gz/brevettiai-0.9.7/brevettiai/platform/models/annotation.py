import logging
import warnings
from itertools import groupby
from typing import Dict, Any, Tuple, List, Union, Literal
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
import pydantic.color as pydantic_color
import shapely.geometry as sgeom
import shapely.ops as sops
from pydantic import BaseModel, Field, conint, validator


from brevettiai.io import io_tools
from brevettiai.utils.polygon_utils import cv2_contour_to_shapely, simplify_polygon

log = logging.getLogger(__name__)

try:
    import cv2
except ImportError:
    warnings.warn("opencv not installed, features for drawing annotations are not available", ImportWarning)


class PolygonFeatures(BaseModel):
    path_length: float
    area: float
    centroid: Tuple[float, float]
    bbox: Tuple[float, float, float, float]
    moments_hu: Tuple[float, float, float, float, float, float, float]

    @classmethod
    def calculate_features(cls, annotation: 'PointsAnnotation'):

        hu_moments = tuple(annotation.hu_moments.flatten())
        return cls(
            path_length=annotation.path_length,
            area=annotation.area,
            bbox=tuple(annotation.bbox),
            centroid=annotation.centroid,
            moments_hu=hu_moments
        )


def flatten_structure(x, name='', out=None):
    out = {} if out is None else out
    x = x.dict() if isinstance(x, BaseModel) else x

    if type(x) is dict:
        for a in x:
            flatten_structure(x[a], name + a + '.', out)
    elif isinstance(x, (list, tuple, np.ndarray)):
        i = 0
        for a in x:
            flatten_structure(a, name + str(i) + '.', out)
            i += 1
    else:
        out[name[:-1]] = x
    return out


class ArrayMeta(type):
    def __getitem__(self, t):
        return type('Array', (PointsArray,), {'inner_type': t})


class PointsArray(np.ndarray, metaclass=ArrayMeta):
    @classmethod
    def from_polygon(cls, polygon):
        return np.stack(polygon.exterior.xy, -1)[:-1].view(cls)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_type

    @classmethod
    def validate_type(cls, val):
        if isinstance(val, np.ndarray):
            assert val.ndim == 2
            assert val.shape[1] == 2
            array = val.astype(cls.inner_type)
        elif isinstance(val, (list, tuple)):
            try:
                array = np.array(tuple((p["x"], p["y"]) for p in val), dtype=cls.inner_type)
            except TypeError:
                array = np.array(tuple((p[0], p[1]) for p in val), dtype=cls.inner_type)
        elif isinstance(val, sgeom.LineString):
            array = np.stack(val.xy, axis=-1)
        else:
            raise NotImplementedError("type not implemented")
        return array.view(PointsArray)

    def dict(self):
        return [{"x": p[0].tolist(), "y": p[1].tolist()} for p in self]


class Color(pydantic_color.Color):
    def __init__(self, value: Union[pydantic_color.ColorType, Tuple]) -> None:
        if isinstance(value, str):
            value = value.replace("hsla", "hsl")
        super().__init__(value)

    @classmethod
    def from_hsl(cls, h, s, l, a=None):
        r, g, b = pydantic_color.hls_to_rgb(h, l, s)
        return cls((255 * r, 255 * g, 255 * b, a))


class Annotation(BaseModel):
    type: str
    label: str
    color: Color
    uuid: UUID = Field(default_factory=uuid4)
    visibility: conint(ge=-1, le=3) = -1
    severity: conint(ge=-1, le=3) = -1
    features: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        validate_assignment = True

    @validator("features", pre=True, allow_reuse=True)
    def none_features_is_default(cls, v):
        return dict() if v is None else v

    @validator("visibility", "severity", pre=True, allow_reuse=True)
    def default_negative_1(cls, v):
        return -1 if v is None else v


class ClassAnnotation(Annotation):
    type: Literal["class"] = "class"


class GroundTruth(BaseModel):
    label: str
    iou: float = -1
    coverage: float = -1
    severity: float = -1

    def dict(self, **kwargs):
        return {"label": self.label, "iou": self.iou}

    @classmethod
    def from_annotation(cls, annotation, target=None):
        iou = -1 if target is None else target.iou(annotation)
        return cls(label=annotation.label, iou=iou)


class PointsAnnotation(Annotation):
    points: PointsArray[np.float32]
    parent: UUID = None
    is_hole: bool = False
    ground_truth: GroundTruth = None
    _shapely: Union[None, sgeom.Polygon] = None
    _centroid: Union[None, Tuple[float, float]] = None
    _moments: Union[None, Dict[str, float]] = None
    _hu_moments: Tuple[float, float, float, float, float, float, float] = None
    _mask = None

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    def clear_calculated(self):
        self._shapely = None
        self._centroid = None
        self._moments = None
        self._mask = None

    def transform_points(self, matrix):
        padded = np.pad(np.array(self.points), ((0, 0), (0, 1)), constant_values=1)
        t_points = np.matmul(matrix, padded.T).T[..., :2]
        self.points = t_points
        self.clear_calculated()

    def dict(self, *args, **kwargs):
        cfg = BaseModel.dict(self, *args, **kwargs)
        if "points" in cfg:
            cfg["points"] = cfg["points"].dict()
        return cfg

    @property
    def bbox(self):
        return np.concatenate((self.points.min(axis=0), self.points.max(axis=0)))

    @property
    def path_length(self):
        return cv2.arcLength(self.points, True)
        # return sum((self._dist(a, b) for a, b in zip(points, np.roll(points, 1))))

    @property
    def area(self):
        return cv2.contourArea(self.points)
        # return sum([a['x'] * b['y'] - a['y'] * b['x'] for (a, b) in zip(points, np.roll(points, 1))]) / 2

    @property
    def centroid(self):
        if self._centroid is None:
            m = self.moments
            m00 = max(m['m00'], 1e-6)
            self._centroid = m['m10'] / m00, m['m01'] / m00
        return self._centroid

    @property
    def moments(self):
        if self._moments is None:
            self._moments = cv2.moments(self.points)
        return self._moments

    @property
    def hu_moments(self):
        if self._hu_moments is None:
            self._hu_moments = cv2.HuMoments(self.moments)
        return self._hu_moments

    @property
    def mask(self):
        if self._mask is None:
            bbox = self.bbox.astype(int)
            mask = np.zeros((bbox[2:] - bbox[:2]).astype(np.int32)[::-1])
            cnt = (self.points - np.amin(self.points, axis=0))[:, np.newaxis, :]
            cv2.drawContours(mask, np.array([cnt]).astype(np.int32), -1, 1, cv2.FILLED)
            self._mask = mask.T
        return self._mask

    @property
    def polygon(self):
        if self._shapely is None:
            self._shapely = sgeom.Polygon(np.concatenate((self.points, self.points[0, None])))
        return self._shapely

    def fix_polygon(self):
        self._shapely = self.polygon.buffer(0)
        return self

    def sample_points(self, tries=100000):
        _min, _max = self.points.min(axis=0), self.points.max(axis=0)
        _range = (_max - _min)
        for i in range(tries):
            p = (np.random.rand(2) * _range) + _min
            if cv2.pointPolygonTest(self.points, tuple(p), False) >= 0:
                yield np.round(p).astype(int)

    def intersection(self, p2):
        if isinstance(p2, PointsAnnotation):
            p2 = p2.polygon
        try:
            return self.polygon.intersection(p2).area
        except Exception:
            return 0

    def iou(self, p2):
        if isinstance(p2, PointsAnnotation):
            p2 = p2.polygon
        inters = self.intersection(p2)
        return inters / (self.polygon.area + p2.area - inters)

    def flat_features(self):
        return flatten_structure(self.features)


class PolygonAnnotation(PointsAnnotation):
    type: Literal["polygon"] = "polygon"


class RectangleAnnotation(PointsAnnotation):
    type: Literal["rectangle"] = "rectangle"

    @property
    def contour(self):
        pt_list = np.array(tuple(map(tuple, self.points)), dtype=np.float32)
        return np.array([pt_list[[0, 0, 1, 1], 0], pt_list[[0, 1, 1, 0], 1]]).T

    @property
    def polygon(self):
        if self._shapely is None:
            self._shapely = sgeom.box(*self.points[:2].flatten())
        return self._shapely

    @property
    def area(self):
        return np.prod(np.abs(np.diff(self.points, axis=0)))


class LineAnnotation(PointsAnnotation):
    type: Literal["line"] = "line"

    @property
    def polygon(self):
        if self._shapely is None:
            self._shapely = sgeom.LineString(self.points)
        return self._shapely


class PointAnnotation(PointsAnnotation):
    type: Literal["point"] = "point"

    def sample_points(self, tries=100000):
        p = self.points.astype(int)[0]
        for i in range(tries):
            yield p


def sub_ious(annotation, polygons):
    iter_ = (polygons.geoms if isinstance(polygons, sgeom.MultiPolygon) else [polygons])
    return max(annotation.iou(polygon) for polygon in iter_)


class ImageAnnotation(BaseModel):
    annotations: List[Union[PolygonAnnotation, RectangleAnnotation, LineAnnotation, PointAnnotation, ClassAnnotation]]
    source: dict = None
    image: dict = None
    metrics: dict = None

    def transform_annotation(self, matrix):
        for annotation in self.annotations:
            annotation.transform_points(matrix)

    def label_map(self):
        lbl_map = {}
        for ann in self.annotations:
            lbl_map.setdefault(ann.label, []).append(ann)
        return lbl_map

    def draw_contours_CHW(self, draw_buffer, label_space=None):
        if label_space is None:
            label_space = {k: v[0].color.as_rgb_tuple() for k, v in self.label_map().items()}
        return draw_contours_CHW(self.annotations, label_space=label_space, draw_buffer=draw_buffer)

    def intersections(self, right):
        left = self.annotations
        right = right.annotations if isinstance(right, ImageAnnotation) else right
        matrix = np.zeros((len(left), len(right)))
        for i, ann1 in enumerate(left):
            for j, ann2 in enumerate(right):
                matrix[i, j] = ann1.intersection(ann2)
        return matrix

    def fix_invalid(self):
        self.annotations = [a if a.polygon is not None and a.polygon.is_valid else a.fix_polygon() for a in
                            self.annotations]
        self.annotations = [a for a in self.annotations if a.polygon is not None and not a.polygon.is_empty]
        return self

    def ious(self, right):
        left = self.annotations
        right = right.annotations if isinstance(right, ImageAnnotation) else right
        matrix = np.zeros((len(left), len(right)))
        for i, ann1 in enumerate(left):
            for j, ann2 in enumerate(right):
                matrix[i, j] = ann1.iou(ann2)
        return matrix

    def to_dataframe(self):
        return pd.DataFrame(map(lambda x: {
            **x.dict(),
            "Defect": "Unmatched" if x.ground_truth is None else x.ground_truth.label,
            "polygon": x.polygon,
            **x.flat_features()
        }, self.annotations))

    def match_annotations(self, b, min_coverage=0.2):
        b = [x for x in b.annotations if isinstance(x, PointsAnnotation) and x.label not in {"TODO"} and not x.is_hole]
        if len(b) > 0:
            label_groups = groupby(b, lambda x: x.label)
            labels, polygons = zip(*map(lambda x: (x[0], sops.unary_union([a.polygon for a in x[1]])), label_groups))
            labels, polygons = np.array(labels), np.array(polygons)
            # Calculate areas, intersections and iou
            intersections = self.intersections(polygons)
            intersection_count = (intersections > 0).sum(-1)

            for ix, count in enumerate(intersection_count):
                if count == 1:
                    annotation = self.annotations[ix]
                    m_ix = np.argmax(intersections[ix])
                    coverage = intersections[ix, m_ix] / annotation.polygon.area
                    label = labels[m_ix]
                    if coverage > min_coverage:
                        annotation.ground_truth = GroundTruth(label=label, coverage=coverage, severity=b[m_ix].severity)
                elif count > 0:
                    annotation = self.annotations[ix]
                    match_mask = intersections[ix] > 0
                    matches = polygons[match_mask]
                    max_iou = [sub_ious(annotation, m) for m in matches]
                    arg_max_iou = np.argmax(max_iou)
                    label = labels[match_mask][arg_max_iou]
                    severity = b[arg_max_iou].severity
                    coverage = intersections[ix, match_mask][arg_max_iou] / annotation.polygon.area

                    if coverage > min_coverage:
                        annotation.ground_truth = GroundTruth(label=label, coverage=coverage, severity=severity)

    @staticmethod
    def extract_features(channel, features, classes, bbox, mask, threshold, sample, CHW, chierarchy, annotations,
                         annotation, get_features):
        try:
            iter(get_features)
        except TypeError as te:
            return annotation  # get_features is not iterable

        for f in get_features:
            if f == "segmentation":
                if CHW:
                    masked = np.where(mask[None], features, np.nan)
                    axis = (1, 2)
                else:
                    masked = np.where(mask[..., None], features, np.nan)
                    axis = (0, 1)

                stats = np.nanpercentile(masked, [10, 50, 90], axis=axis).T
                stats2 = np.array(
                    [np.nanmin(masked, axis=axis), np.nanmean(masked, axis=axis), np.nanmax(masked, axis=axis)]).T
                stats = np.hstack((stats, stats2))

                seg_names = ["10th_percentile", "median", "90th_percentile", "min", "mean", "max"]
                annotation.features["segmentation"] = {k: dict(zip(seg_names, v.tolist())) for k, v in
                                                       zip(classes, stats)}
                annotation.visibility = int(sum(np.linspace(threshold, 1, 4)[:-1] <= stats[channel, 1]))
            elif f == "polygon":
                annotation.features["polygon"] = PolygonFeatures.calculate_features(annotation)

        return annotation

    @classmethod
    def from_path(cls, path, io=io_tools, errors="raise"):
        try:
            return cls.parse_raw(io.read_file(path))
        except Exception as ex:
            if errors == "raise":
                raise ex
            return None

    @classmethod
    def from_segmentation(cls, segmentation, classes, sample, image_shape, tform=None,
                          threshold=0.5, simplify=False,
                          output_classes=None, CHW=False, feature_func=None, get_features=None, max_annotations=np.inf,
                          color_list=None,
                          feature_map=None):
        color_list = color_list if color_list is not None else ['blue', 'cyan', 'goldenrod', 'green', 'magenta',
                                                                'orange', 'red', 'violet']
        feature_map = feature_map if feature_map is not None else segmentation
        processing_kernel = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1],
                                      [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]], np.uint8)

        if not CHW:
            segmentation = np.transpose(segmentation, [2, 0, 1])
            feature_map = np.transpose(feature_map, [2, 0, 1])

        annotations = []
        for channel, class_ in enumerate(classes):
            if output_classes and class_ not in output_classes:
                continue
            channel_annotations = {}
            color = color_list[channel % len(color_list)]

            features = segmentation[channel]
            try:
                threshold_ = threshold[channel]
            except TypeError:
                threshold_ = threshold
            mask = (features > threshold_).astype(np.uint8)

            # cleanup
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, processing_kernel)

            # Find labels and contours
            # Note labels index and contour id does not match
            num_labels, labels = cv2.connectedComponents(mask)
            # https://docs.opencv.org/master/d9/d8b/tutorial_py_contours_hierarchy.html
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Keep only 'max_annotations' biggest contours
            contour_area = [cv2.contourArea(cnt) for cnt in contours]
            remove_mask = np.full(len(contours), False)
            if len(contours) > max_annotations:
                remove_mask[np.argpartition(contour_area, -max_annotations)[:-max_annotations]] = True
            if len(contours):
                for ix, (contour, chierarchy, remove_item) in enumerate(zip(contours, hierarchy[0], remove_mask)):
                    if remove_item:
                        continue
                    # get bounding box
                    min_, max_ = contour.min((0, 1)), contour.max((0, 1))
                    # get label id of contour
                    clabel = labels[contour[0, 0, 1], contour[0, 0, 0]]

                    # extract masks and features in bbox
                    cmask = labels[min_[1]:max_[1] + 1, min_[0]:max_[0] + 1] == clabel
                    cfeatures = feature_map[:, min_[1]:max_[1] + 1, min_[0]:max_[0] + 1]

                    parent_annotation_ix, parent, is_hole = chierarchy[3], None, False
                    # if parent exists
                    if parent_annotation_ix >= 0:
                        parent = channel_annotations.get(parent_annotation_ix)
                        is_hole = False if parent is None else not parent.is_hole
                    else:
                        is_hole = False

                    polygon = cv2_contour_to_shapely(contour)
                    if simplify:
                        polygon = simplify_polygon(polygon)
                    cnt = np.stack(polygon.exterior.xy, 1)

                    # Rescale contours to input shape
                    if tform is not None:
                        pts = np.pad(cnt.astype(np.float32).reshape(-1, 2), [[0, 0], [0, 1]], constant_values=1)
                        cnt = (tform @ pts.T)[:2].T

                    cnt = cnt.round(2)

                    annotation = PolygonAnnotation(
                        label=class_,
                        points=cnt,
                        is_hole=is_hole,
                        parent=None if parent is None else parent.uuid,
                        color=Color("dark" + color) if False and is_hole else color,
                    )

                    if get_features is not None:
                        annotation = (feature_func or ImageAnnotation.extract_features)(
                            channel=channel,
                            features=cfeatures,
                            classes=classes,
                            bbox=(slice(min_[1], max_[1] + 1), slice(min_[0], max_[0] + 1)),
                            mask=cmask,
                            threshold=threshold_,
                            sample=sample,
                            CHW=True,
                            chierarchy=chierarchy,
                            annotations=annotations,
                            annotation=annotation,
                            get_features=get_features
                        )

                    channel_annotations[ix] = annotation
            annotations.extend(channel_annotations.values())

        return cls(annotations=annotations, image=dict(
            fileName=sample.get("path"),
            sampleId=sample.get("sample_id"),
            etag=sample.get("etag"),
            width=int(image_shape[1]),
            height=int(image_shape[0])
        ))

    def __repr__(self):
        return f"ImageAnnotation({self.image})"


def draw_contours_CHW(annotations, draw_buffer, label_space=None):
    lbl_map = {}
    for ann in annotations:
        lbl_map.setdefault(ann.label, []).append(ann)

    for lbl, color in label_space.items():
        contours = []
        for ann in annotations:
            if isinstance(ann, PointsAnnotation) and (
                    lbl == ann.label or
                    (isinstance(lbl, tuple) and np.any([lbl_ii == ann.label for lbl_ii in lbl]))
            ):
                contours.append(ann.points.astype(np.int32))

        # Draw contours
        if len(contours):
            color = color if isinstance(color, (tuple, list)) else color.tolist()
            for i, c in enumerate(color):
                if c != 0:
                    cv2.drawContours(draw_buffer[i], contours, -1, c, thickness=cv2.FILLED)
    return draw_buffer
