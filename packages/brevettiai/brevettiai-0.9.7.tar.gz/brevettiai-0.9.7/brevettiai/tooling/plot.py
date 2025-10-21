from typing import Union

import shapely.geometry as sgeom
from brevettiai.datamodel.image_annotation import ImageAnnotation, AnnotationTypes
import matplotlib.pyplot as plt
from matplotlib.pyplot import *

# Ensure plt functions are seen
__all__ = ["show", "imshow", "plot", "scatter"]


def annotation(obj: Union[ImageAnnotation, AnnotationTypes]):
    """Plot an Image Annotation"""
    if hasattr(obj, "annotations"):
        obj = obj.annotations
    obj = obj if type(obj) == list else [obj]
    for annotation in obj:
        shapely(annotation.geometry, annotation.color_obj.as_hex())


def shapely(geom, color=None, hole_color=None):
    """Plot a shapely geometric object"""
    if geom.is_empty:
        return

    if hole_color is None:
        hole_color = color

    if geom.geom_type == "Point":
        plt.plot(*geom.xy, marker="x", color=color)
    elif geom.geom_type == "MultiLineString":
        for g in geom.geoms:
            shapely(g, color=color, hole_color=hole_color)
    elif geom.geom_type in ("LineString", "LinearRing"):
        plt.plot(*geom.xy, color=color)
    elif geom.geom_type == "Polygon":
        shapely(geom.exterior, color=color)
        for hole in geom.interiors:
            shapely(hole, color=hole_color)
    elif geom.geom_type == "MultiPoint":
        if len(geom.geoms) > 1:
            geom = sgeom.LineString(geom.geoms)
        else:
            geom = geom.geoms[0]
        plt.plot(*geom.xy, marker="x", linestyle='', color=color)
    elif geom.geom_type == "MultiPolygon":
        for polygon in geom.geoms:
            shapely(polygon, color=color, hole_color=hole_color)