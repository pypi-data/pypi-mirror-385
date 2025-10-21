import requests

from pydantic import parse_raw_as
from typing import List, Union

from brevettiai.datamodel.web_api_types import AnnotationEntry
from brevettiai.datamodel.image_annotation import ImageAnnotation


def ok(r):
    r.raise_for_status()
    return r


def get_dataset_annotations(host, dataset, image_path=None, model_id=None, test_report_id=None,
                            get_fn=None, **kwargs):
    if get_fn is None:
        get_fn = requests.get

    dataset_id = dataset.id if hasattr(dataset, "id") else dataset

    endpoint = f"{host}/api/data/{dataset_id}/annotations"

    parameters = {k: v for k, v in {
        "imagePath": image_path,
        "modelId": model_id,
        "testReportId": test_report_id
    }.items() if v is not None}
    r = ok(get_fn(endpoint, params=parameters, **kwargs))
    return parse_raw_as(Union[List[AnnotationEntry], AnnotationEntry], r.content)


def update_annotation(host, dataset, annotation, image_path, annotation_name=None, post_fn=None, **kwargs):
    if post_fn is None:
        post_fn = requests.post

    dataset_id = dataset.id if hasattr(dataset, "id") else dataset

    payload = annotation.json(by_alias=True)
    endpoint = f"{host}/api/data/{dataset_id}/annotations"

    if annotation_name is None:
        entry = create_annotation(host, dataset_id, image_path, post_fn=post_fn)
        annotation_name = sorted(entry.annotation_files.keys())[-1]
    parameters = {
        "imagePath": image_path,
        "annotationFileName": annotation_name,
    }
    r = ok(post_fn(endpoint, params=parameters, data=payload, headers={"Content-Type": "application/json"}, **kwargs))
    return parse_raw_as(ImageAnnotation, r.content)


def create_annotation(host, dataset, image_path, annotation_name=None, post_fn=None, **kwargs):
    if post_fn is None:
        post_fn = requests.post

    dataset_id = dataset.id if hasattr(dataset, "id") else dataset

    endpoint = f"{host}/api/data/{dataset_id}/createannotationfile"
    parameters = {k: v for k, v in {
        "imagePath": image_path,
        "annotationFileName": annotation_name,
    }.items() if v is not None}
    r = ok(post_fn(endpoint, params=parameters, **kwargs))

    entry = parse_raw_as(AnnotationEntry, r.content)
    entry.image_path = image_path
    return entry


def delete_annotation(host, dataset, image_path, annotation_name, delete_fn=None, **kwargs):
    if delete_fn is None:
        delete_fn = requests.delete

    dataset_id = dataset.id if hasattr(dataset, "id") else dataset

    endpoint = f"{host}/api/data/{dataset_id}/annotations"

    parameters = {
        "imagePath": image_path,
        "annotationFileName": annotation_name,
    }
    r = ok(delete_fn(endpoint, params=parameters, **kwargs))
