import requests

from brevettiai.datamodel import Dataset
from brevettiai.platform import PlatformAPI


def copy_image(platform: PlatformAPI, dataset: Dataset, image_path: str, target_image_path: str, skip_image=False):
    """Copy image with annotations, Tiles are not copied"""
    if not skip_image:
        current_image = dataset.bucket / image_path
        current_image.copy(dataset.bucket / target_image_path, force_overwrite_to_cloud=True)

    entry = platform.get_dataset_annotations(dataset, image_path=image_path)
    for name, ann in entry.annotation_files.items():
        try:
            platform.create_annotation(dataset, image_path=target_image_path, annotation_name=name)
        except requests.HTTPError:
            pass
        platform.update_annotation(dataset, image_path=target_image_path, annotation_name=name, annotation=ann)


def delete_image(platform: PlatformAPI, dataset: Dataset, image_path: str, missing_ok=True):
    """Delete image entry in a platform dataset"""
    entry = platform.get_dataset_annotations(dataset, image_path=image_path)
    for name, ann in entry.annotation_files.items():
        platform.delete_annotation(dataset, image_path, name)

    file = dataset.bucket / image_path
    file.remove(missing_ok=missing_ok)
