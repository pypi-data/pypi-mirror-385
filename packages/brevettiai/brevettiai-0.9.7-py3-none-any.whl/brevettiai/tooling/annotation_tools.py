import random
from collections import defaultdict
from typing import List, Optional

import cv2
import numpy as np
import shapely.geometry as sgeom
from shapely.affinity import affine_transform

from brevettiai.datamodel.image_annotation import PolygonAnnotation


def affine_transform_coefficients(matrix):
    return matrix[0, 0], matrix[0, 1], matrix[1, 0], matrix[1, 1], matrix[0, 2], matrix[1, 2]


def get_random_points_in(geom, nmax=1000):
    if geom.geom_type == "Polygon":
        if geom.area == 0:
            yield from random_point_on_border_of(geom.exterior, nmax)
        else:
            yield from random_point_contained_in(geom, nmax)
    elif geom.geom_type == "LineString":
        yield from random_point_on_border_of(geom, nmax)
    elif geom.geom_type == "Point":
        yield geom


def random_point_contained_in(geom, nmax):
    """Return points contained in geometry"""
    minx, miny, maxx, maxy = geom.bounds
    while True:
        p = sgeom.Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if geom.contains(p):
            yield p
            nmax -= 1
            if nmax <= 0:
                return


def random_point_on_border_of(geom, nmax):
    """Return points on the border of a geometry"""
    while True:
        yield geom.line_interpolate_point(random.uniform(0, 1), normalized=True)
        nmax -= 1
        if nmax <= 0:
            return


def get_inside_points(geom, n=10, nmax=1000):
    return np.vstack([p[1].coords for p in zip(range(n), get_random_points_in(geom))])


def mask_to_polygons(mask, min_area=0, min_area_hole=25, max_count=200):
    """Convert a mask ndarray (binarized image) to Multipolygons"""
    # first, find contours with cv2: it's much faster than shapely
    contours, hierarchy = cv2.findContours(mask.astype(np.uint8),
                                  cv2.RETR_CCOMP,
                                  cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return []

    # Calculate areas for all contours
    areas = np.array([cv2.contourArea(cnt) for cnt in contours])

    # Filter elements
    is_hole = hierarchy[0, :, -1] >= 0
    mask = areas >= np.where(is_hole, min_area_hole, min_area)
    selected = np.arange(len(contours))[mask]

    # Filter by sorted by max count
    if len(selected) > max_count:
        selected = selected[np.argpartition(areas[mask], -max_count)[-max_count:]]

    # Arrange children
    selected_is_hole = is_hole[selected]
    cnt_children = defaultdict(list)
    for ix in selected[selected_is_hole]:
        cnt_children[hierarchy[0, ix, -1]].append(contours[ix])

    # create actual polygons
    all_polygons = []
    for idx in selected[~selected_is_hole]:
        cnt = contours[idx]
        assert cnt.shape[1] == 1
        if len(cnt) == 1:
            geom = sgeom.box(*cnt[0, 0, :]-0.5, *cnt[0, 0, :]+0.5)
        elif len(cnt) == 2:
            geom = sgeom.LineString(cnt[:, 0, :]).buffer(0.5, quad_segs=1, cap_style=3).oriented_envelope
        else:
            geom = sgeom.Polygon(
                shell=cnt[:, 0, :],
                holes=[c[:, 0, :] for c in cnt_children.get(idx, [])]
            ).buffer(0.5, quad_segs=1).simplify(0.5, preserve_topology=False)

        if not geom.is_empty:
            all_polygons.append(geom)
    return all_polygons


def simplify_polygon(polygon, max_point_density=1/25, max_points=20, levels=(1, 2, 4, 8, 16, 24)):
    for epsilon in levels:
        coords = len(polygon.exterior.coords)
        if coords / polygon.exterior.length < max_point_density or coords <= max_points:
            break
        polygon = polygon.simplify(epsilon, preserve_topology=True)
    return polygon


def extract_annotations(segmentation, classes: List, threshold=0.5, output_classes: Optional[List] = None,
                        transform=None, colors=None, extract_args=None, simplify_args=None):
    mask = (segmentation > threshold).astype(np.uint8)

    if type(transform) == np.ndarray:
        transform = affine_transform_coefficients(transform)

    # Ensure channel dimension exists
    if mask.ndim == 2:
        mask = mask[..., None]

    colors = colors or {}

    # Build annotation
    annotations = []
    for channel, class_ in enumerate(classes):
        if output_classes and class_ not in output_classes:  # Skip class
            continue

        polys = mask_to_polygons(mask[..., channel], **(extract_args or {}))

        if not polys:  # Nothing to append
            continue

        shared_properties = dict(
            label=class_,
        )
        color = colors.get(class_, None)
        if color:
            shared_properties["color"] = color

        if transform is not None:
            polys = [affine_transform(p, transform) for p in polys]

        simplify_args = simplify_args or {}
        polys = [simplify_polygon(p, **simplify_args) for p in polys]

        for polygon in polys:
            boundary = polygon.boundary
            if boundary.geom_type == "MultiLineString":
                geometries = boundary.geoms
            else:
                geometries = [boundary]
            for geometry in geometries:
                annotations.append(PolygonAnnotation(geometry=sgeom.Polygon(geometry), **shared_properties))

    return annotations
