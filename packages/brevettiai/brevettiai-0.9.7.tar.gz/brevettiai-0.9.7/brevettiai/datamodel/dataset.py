from pydantic import BaseModel, Field, PrivateAttr
from uuid import uuid4
from typing import Optional, List, Union, Dict
from datetime import datetime
import urllib

from brevettiai.datamodel import CamelModel
from brevettiai.datamodel.tag import Tag
from brevettiai.io import AnyPath, get_default_s3_client_manager, S3Path

IMAGE_SUFFIXES = frozenset((".tif", ".bmp", ".jpeg", ".jpg", ".png"))


def filter_suffix_in(paths, allowed_suffixes):
    allowed_suffixes = set(allowed_suffixes)
    for path in paths:
        if path.suffix.lower() in allowed_suffixes:
            yield path


class Dataset(BaseModel):
    """
    Model defining a dataset on the Brevetti platform
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    bucket: Optional[Union[AnyPath, S3Path]] = Field(default=None)
    name: str
    created: datetime = Field(default=datetime.utcnow())
    locked: bool = False
    reference: Optional[str] = ""
    notes: Optional[str] = ""
    tags: List[Tag] = Field(default_factory=list, description="tags on dataset")

    _backend = PrivateAttr(default=None)

    def __init__(self, backend=None, credentials=None, **data) -> None:
        super().__init__(**data)

        self._backend = backend

        if self.bucket is None and backend is not None:
            self.bucket = AnyPath(backend.resource_path(self.id))

        if credentials:
            self.resolve_access_rights(credentials)

    def resolve_access_rights(self, credentials):
        if hasattr(credentials, "s3_credentials"):
            credentials = credentials.s3_credentials

        manager = get_default_s3_client_manager()
        manager.resolve_access_rights(
            partial_path=self.bucket,
            credentials_getter=lambda: credentials.get_credentials(resource_id=self.id, resource_type="dataset")
        )

    def disable_access_rights(self):
        try:
            self.bucket.client.disable()
        except AttributeError:
            pass

    @property
    def backend(self):
        return self._backend

    def get_uri(self):
        return f"{self.backend.host}/data/{self.id}"

    def get_sample_uri(self, path):
        relative_path = str(AnyPath(path).relative_to(self.bucket))
        return f"{self.backend.host}/download?path={urllib.parse.quote(relative_path, safe='')}"

    def iter(self, path: Optional[str] = None, after_hidden=True, include_dirs=False, max_items=None,
             recursive=True, file_types=None, **kwargs):

        if path is not None:
            path = self.bucket / path
        else:
            path = self.bucket

        if type(file_types) == str:
            file_types = {file_types}

        if "start_after" not in kwargs:
            kwargs["start_after"] = ".\uFFFD" if after_hidden else None

        items = path.iterdir(recursive=recursive, include_dirs=include_dirs, max_items=max_items, **kwargs)

        if file_types:
            items = filter_suffix_in(items, file_types)

        return items

    def iter_images(self, path: Optional[str] = None, max_items=None, file_types=IMAGE_SUFFIXES):
        """Utility function for iterating over images in the dataset"""
        return self.iter(after_hidden=True, include_dirs=False,
                         recursive=True, max_items=max_items, file_types=file_types)


class DatasetObject(CamelModel):
    """
    object located in a dataset
    """
    path: str
    bici_reference: str = ""
    dataset_id: Optional[str] = Field(default=None, exclude=True)
    item: Optional['DatasetItem'] = Field(default=None, exclude=True)


class DatasetItemMetadata(CamelModel, extra="allow"):
    machine: Optional[str]
    tv: Optional[str]
    inspection_type: Optional[str]
    camera_view: Optional[str]
    category: Optional[str]
    shape: Optional[Dict[str, int]]
    run: Optional[int]
    sample_id: Optional[str]


class DatasetItem(CamelModel):
    dataset_id: str = None
    item_id: str
    objects: List[DatasetObject]
    metadata: DatasetItemMetadata = Field(default_factory=DatasetItemMetadata)
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    labels: List[str] = Field(default_factory=list)


DatasetObject.update_forward_refs()
