import h5py
import importlib_metadata
import sys
from pydantic import BaseModel, Field, parse_obj_as, root_validator
from typing import Optional, Type, Dict, Literal
from brevettiai import Module
from brevettiai import __version__ as brevettiai_version

from brevettiai.io.h5_metadata import extract_metadata, get_metadata as h5_metadata


def get_version(package):
    try:
        return importlib_metadata.version(package)
    except importlib_metadata.PackageNotFoundError:
        return "<not found>"


def _get_environment():
    return {
        "brevettiai": brevettiai_version,
        "python": sys.version,
        **{
            x: v
            for x in ["tensorflow", "brevettiai", "mopsus", "image_segmentation"]
            if (v := get_version(x)) != "<not found>"
        }
    }


class ModelMetadata(BaseModel):
    # Metadata file fields
    type: Optional[Literal["ModelMetadata"]] = Field(default=None, description="Object specifier")
    version: str = Field(default="2.0", const=True, description="Metadata version number marker")

    # Model related fields
    id: str = Field(description="unique id of model")
    name: str = Field(description="Name of model")
    created: str = Field(description="timestamp of producing code")
    producer: str = Field(description="Name of producing code")
    environment: Dict[str, str] = Field(default_factory=dict,
                                        description="Environment info at time of serialization,"
                                                    "updated when .json is called if empty")

    @root_validator(pre=True, allow_reuse=True)
    def get_type(cls, values):
        # Update V1 types
        if {"host_name", "run_id"}.issubset(values.keys()):
            del values["host_name"]
            values["created"] = values.pop("run_id")

        # Set type if not given to ensure it is set
        if "type" not in values or values["type"] is None:
            values["type"] = cls.__name__
        return values

    class Config:
        json_encoders = {
            Module: lambda x: x.get_config()
        }

    @classmethod
    def from_metadata(cls, obj, **kwargs):
        return cls.parse_obj({**obj.dict(exclude={"type", "version"}), **kwargs})

    def update_environment(self):
        self.environment = _get_environment()

    def json(self, *args, **kwargs) -> str:
        if not self.environment:
            self.update_environment()
        return super().json(*args, **kwargs)


def get_metadata(file: str, metadata_type: Type[ModelMetadata] = ModelMetadata):
    if isinstance(file, h5py.File):
        return parse_obj_as(metadata_type, extract_metadata(file))
    if file.endswith(".h5"):  # file is a string specifying the path
        return parse_obj_as(metadata_type, h5_metadata(file))
    else:
        raise NotImplementedError(f"Getting metadata from '{file}' not implemented")
