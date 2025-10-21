from typing import Literal, Dict, Any, List, Optional

import cv2
import numpy as np
import tensorflow as tf
from pydantic import Field, PrivateAttr, validator, BaseModel

from brevettiai.data.data_generator import DataGeneratorMap
from brevettiai.data.image import ImageKeys
from brevettiai.data.image.image_loader import CropResizeProcessor
from brevettiai.data.tf_types import BBOX
from brevettiai.datamodel import ImageAnnotation


def get_poly_points(annotations, scale=1, offset=(0, 0), shift=0):
    for annotation in annotations:
        if annotation.type in ("polygon", "rectangle"):
            try:
                pts = (np.asarray(annotation.geometry.exterior.coords) + offset) * (scale * 2**shift)
            except ValueError as ex:
                pass  # Fail silently
            yield pts.astype(np.int32)


class AnnotationLoader(DataGeneratorMap, BaseModel):
    """
    Basic File loading module for DataGenerator
    """
    type: Literal["AnnotationLoader"] = "AnnotationLoader"

    input_map: Dict[str, str] = Field(
        default={
            "annotation": "annotation_path",
            "shape": "_image_file_shape",
            "bbox": ImageKeys.BOUNDING_BOX,
            "zoom": ImageKeys.ZOOM,

        },
        description="function kwarg -> key mapping")

    output_key: str = Field(default="annotation")

    classes: List[str] = Field()
    mapping: Dict[str, str] = Field(default_factory=dict,
                                    description="mapping from annotation label to class, use '|' to signal multiclass")
    postprocessor: Optional[CropResizeProcessor] = Field(default_factory=None, exclude=True)

    _annotations: Dict[str, ImageAnnotation] = PrivateAttr(default_factory=dict)
    _label_space = PrivateAttr(default=None)

    def __init__(self, annotations, **data) -> None:
        super().__init__(**data)
        self._annotations.update(annotations)

    @validator('input_map', pre=True, allow_reuse=True)
    def combine_partial_input_map_with_default(cls, v, field):
        return {**field.default, **v}

    @validator('mapping', each_item=True, pre=True, allow_reuse=True)
    def convert_non_str_to_pipe_separated_string(cls, v):
        if not isinstance(v, str):
            return "|".join(v)
        return v

    @property
    def apply_unbatched(self):
        """When using in datagenerator, do so on samples, not batches"""
        return True

    @property
    def label_space(self):
        assert self.classes is not None
        if self._label_space is not None:
            return self._label_space

        self._label_space = {}
        targets = dict(zip(self.classes, 255*np.eye(len(self.classes))))
        self._label_space.update(targets)
        for label, class_descriptor in self.mapping.items():
            # Separate multiclass to classes
            classes = [x for x in class_descriptor.split("|") if x in self.classes]
            # map classes to
            if classes:
                self._label_space[label] = np.max(tuple(targets[c] for c in classes), 0)
        return self._label_space

    def _parse_annotation(self, annotation, shape, scale, offset):
        if type(annotation) == np.ndarray:
            annotation = annotation.item()
        if type(annotation) == bytes:
            annotation = annotation.decode()

        channels = len(self.classes)
        label_space = self.label_space
        img_annotation = self._annotations[annotation]

        annotation_classes = {}
        for a in img_annotation.annotations:
            if a.label in label_space:
                annotation_classes.setdefault(a.label, []).append(a)

        offset_xy = offset[::-1]
        scale_xy = scale[::-1]
        img_mask = np.zeros((channels, shape[0], shape[1]), np.uint8)
        for class_, annotations in annotation_classes.items():
            fill = label_space[class_]
            pts = list(get_poly_points(annotations, offset=offset_xy, scale=scale_xy, shift=8))
            for mask, color in zip(img_mask, fill):
                if color:
                    cv2.fillPoly(mask, pts, color, shift=8, lineType=cv2.LINE_AA)
        return img_mask

    def map(self, annotation: str, postprocess: bool = True,
            zoom: float = 1, bbox: BBOX = BBOX(), shape=(128, 128)) -> Dict[str, Any]:
        if type(bbox) != BBOX:
            bbox = BBOX.build(bbox)

        bbox_shape = bbox.shape
        shape = shape[:2]
        shape = tf.where(tf.convert_to_tensor(bbox_shape) > 1, bbox_shape, shape)

        if postprocess and self.postprocessor is not None:
            sy, sx = self.postprocessor.scale(shape[0], shape[1])
            zoom = tf.cast(zoom, tf.float32)
            sy = tf.cast(sy, tf.float32)
            sx = tf.cast(sx, tf.float32)
            scale_ = (1 / (sy * zoom), 1 / (sx * zoom))
            offset = (-self.postprocessor.roi_vertical_offset, -self.postprocessor.roi_horizontal_offset)
            shape = self.postprocessor.output_size(shape[0], shape[1])
        else:
            offset = (0, 0)
            scale_ = (1 / zoom, 1 / zoom)

        offset = tf.constant(offset) - tuple(bbox)[:2]

        img_annotation = tf.numpy_function(self._parse_annotation,
                                        [annotation, (shape[0], shape[1]), scale_, offset],
                                        np.uint8, name="parse_segmentation2")

        if not isinstance(shape, tf.Tensor):
            img_annotation = tf.ensure_shape(img_annotation, (len(self.classes), shape[0], shape[1]))
        else:
            img_annotation = tf.ensure_shape(img_annotation, (len(self.classes), None, None))
        img_annotation = tf.transpose(img_annotation, [1, 2, 0]) / 255

        return {self.output_key: img_annotation}

    def __call__(self, x, *args, **kwargs):
        """Add loaded data to the output key"""
        kwargs = {kwarg: x[key] for kwarg, key in self.input_map.items() if key in x}
        x.update(self.map(**kwargs))
        return x
