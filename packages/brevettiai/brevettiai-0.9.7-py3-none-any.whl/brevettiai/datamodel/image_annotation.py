from typing import List, Dict, Any, Optional, Literal, Union
from uuid import uuid4

import numpy as np
import shapely.errors
import shapely.geometry as sgeom
from pandas._libs.lib import dicts_to_array
from pydantic import Field, conint, UUID4, root_validator, validator

from brevettiai.datamodel import CamelModel
from brevettiai.datamodel.color import get_color, Color


class Annotation(CamelModel):
    type: str
    label: str
    color: str = Field(default_factory=get_color)
    uuid: UUID4 = Field(default_factory=uuid4)
    visibility: Optional[conint(ge=-1, le=3)]
    severity: Optional[conint(ge=-1, le=3)]
    features: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @property
    def color_obj(self):
        return Color(value=self.color)

    def __repr__(self):
        return f"{type(self).__name__}(label={self.label})"


class ClassAnnotation(Annotation):
    type: Literal["class"] = "class"


def _points_encoder(geometry):
    return [dict(x=x, y=y) for x, y in np.asarray(geometry.coords)]


_json_encoders = {
    sgeom.Polygon: lambda x: _points_encoder(x.boundary)[:-1],
    sgeom.LineString: _points_encoder,
    sgeom.Point: _points_encoder,
}


class GeometryAnnotation(Annotation):
    geometry: sgeom.Polygon = Field(exclude=True)

    @property
    def points(self):
        return self.Config.json_encoders[type(self.geometry)](self.geometry)

    def dict(self, *args, **kwargs):
        obj = super().dict(*args, **kwargs)

        include = kwargs.get("include") or {"points"}
        exclude = kwargs.get("exclude") or set()
        if "points" in include - exclude:
            obj["points"] = self.points
        return obj

    class Config:
        underscore_attrs_are_private = True
        arbitrary_types_allowed = True
        json_encoders = _json_encoders


class PolygonAnnotation(GeometryAnnotation):
    type: Literal["polygon"] = "polygon"

    @root_validator(pre=True, allow_reuse=True)
    def parse_geometry(cls, values):
        type_ = values.get("type", None)
        if not (type_ is None or type_ == "polygon"):
            raise ValueError("type not allowed")

        if "color" not in values:
            values["color"] = get_color(values["label"])

        if "geometry" in values:
            return values

        pts = dicts_to_array(values["points"], ["x", "y"]).astype(float)
        try:
            values["geometry"] = sgeom.Polygon(pts)
        except shapely.errors.GEOSException as ex:
            raise ValueError("Invalid geometry") from ex
        return values


class RectangleAnnotation(GeometryAnnotation):
    type: Literal["rectangle"] = "rectangle"

    @root_validator(pre=True, allow_reuse=True)
    def parse_geometry(cls, values):
        type_ = values.get("type", None)
        if type is None or type_ != "rectangle":
            raise ValueError("type not allowed")

        if "color" not in values:
            values["color"] = get_color(values["label"])

        if "geometry" in values:
            return values

        pts = dicts_to_array(values["points"], ["x", "y"]).astype(float)
        values["geometry"] = sgeom.box(*pts.min(0), *pts.max(0))
        return values

    class Config:
        json_encoders = {
            sgeom.Polygon: lambda p: [dict(x=x, y=y) for x, y in np.array(p.bounds).reshape(2, -1)]
        }


class LineAnnotation(GeometryAnnotation):
    type: Literal["line"] = "line"
    geometry: sgeom.LineString = Field(exclude=True)

    @root_validator(pre=True, allow_reuse=True)
    def parse_geometry(cls, values):
        type_ = values.get("type", None)
        if type is None or type_ != "line":
            raise ValueError("type not allowed")

        if "color" not in values:
            values["color"] = get_color(values["label"])

        if "geometry" in values:
            return values

        try:
            pts = dicts_to_array(values["points"], ["x", "y"]).astype(float)
            values["geometry"] = sgeom.LineString(pts)
        except Exception as ex:
            raise ValueError("Error parsing line") from ex

        return values


class PointAnnotation(GeometryAnnotation):
    type: Literal["point"] = "point"
    geometry: sgeom.Point = Field(exclude=True)

    @root_validator(pre=True, allow_reuse=True)
    def parse_geometry(cls, values):
        type_ = values.get("type", None)
        if type is None or type_ != "point":
            raise ValueError("type not allowed")

        if "color" not in values:
            values["color"] = get_color(values["label"])

        if "geometry" in values:
            return values
        point = values["points"][0]
        values["geometry"] = sgeom.Point((point["x"], point["y"]))

        return values


AnnotationTypes = Union[
    PolygonAnnotation,
    RectangleAnnotation,
    LineAnnotation,
    PointAnnotation,
    ClassAnnotation,
    Dict,
]


class Image(CamelModel):
    file_name: Optional[str]
    height: int
    width: int

    sample_id: Optional[str]
    etag: Optional[str]


class AnnotationSource(CamelModel):
    model_id: str
    is_valid: bool = Field(default=True, description="Is all needed data present, or are any frames missing")
    used_in_training: Optional[bool]


class ImageAnnotation(CamelModel):
    annotations: List[AnnotationTypes] = Field(default_factory=list)
    image: Optional[Image]
    source: Optional[AnnotationSource]
    metrics: Optional[Dict[str, Union[str, float, int]]]

    @validator("annotations", pre=True)
    def set_none_annotations(cls, annotations):
        return annotations or []

    def __repr__(self):
        return f"ImageAnnotation({self.image})"
