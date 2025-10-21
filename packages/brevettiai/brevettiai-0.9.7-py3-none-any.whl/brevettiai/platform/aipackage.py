import hashlib
import logging
import os
import re
import shutil

from dataclasses import dataclass
from typing import Dict, ClassVar, Optional
from io import BytesIO

from pydantic import Field

from brevettiai.io import AnyPath
from brevettiai.model import ModelMetadata
from brevettiai.platform import Job
from brevettiai.utils.model_version import get_model_version
import py7zr

log = logging.getLogger(__name__)

MSG_OPEN_ERROR = "Error opening archive"


@dataclass
class AIPackageAsset:
    """
    Data holder for file names and hashes of assets in model archive
    """
    file: str
    hash: str


class AIPackageMetadata(ModelMetadata):
    """
    Metadata for model archives
    adding an assets field for users of the archive to check if it contains what is needed
    """
    AIPACKAGE_VERSION: ClassVar[str] = "1.0"
    """Version of ai package"""

    type: Optional[str]

    version: str = Field(default=AIPACKAGE_VERSION, const=True, description="aipackage version number marker")

    assets: Dict[str, AIPackageAsset] = Field(default_factory=dict,
                                              description="Key value pairs of name and path to asset")


class AIPackage:
    """
    Helps to create archives with different assets and their metadata
    """
    METADATA_URI: ClassVar[str] = "metadata.json"
    """location of metadata file"""

    def __init__(self, path=None, metadata: AIPackageMetadata = None, job: Job = None, password: str = None):

        """
        Initialize ai package.
        Can use job or metadata as source, if neither are given metadata is loaded from current archive

        Notes:
            * Use the context manager to write assets.

        Usage:
            in Job.run:

            ```python
            archive = AIPackage(job=self)
            with model_archive.open_write() as writer:
                writer.add_asset(name="onnx", arcname="model.onnx", file=self.temp_path("model.onnx"))

            with archive.open_read() as reader:
                with reader.get_asset("onnx") as fp:
                    data = fp.read()

            ...
            return archive.upload(self)
            ```

        Args:
            path: location of archive (Must end with .aipkg), if job given and path is None f"{job.name}.aipkg" is chosen
            metadata: optional AIPackage metadata for new packages
            job: optional job to gather metadata from if metadata keyword is missing
            password: optional password to protect the archive. default = None
        """
        path = path or job.temp_path / f"{re.sub('[^-a-zA-Z0-9_.()]+', '_', job.name).lower()}.aipkg"
        self.path = AnyPath(path)
        self.password = password

        try:
            if metadata is not None:
                self.metadata = AIPackageMetadata.parse_obj(metadata)
            elif job is not None:
                self.metadata = AIPackageMetadata.parse_obj(job.get_metadata())
                if self.path.exists():
                    with py7zr.SevenZipFile(self.path, 'r', password=self.password) as arc:
                        targets = arc.read(targets=AIPackage.METADATA_URI)
                        self.metadata = AIPackageMetadata.parse_raw(targets[AIPackage.METADATA_URI].read())
            else:
                if not self.path.exists():
                    raise TypeError("Model archive needs 'metadata' to create archive")
                with py7zr.SevenZipFile(self.path, 'r', password=self.password) as arc:
                    targets = arc.read(targets=AIPackage.METADATA_URI)
                    self.metadata = AIPackageMetadata.parse_raw(targets[AIPackage.METADATA_URI].read())
        except py7zr.Bad7zFile as ex:
            raise IOError(MSG_OPEN_ERROR) from ex
        except py7zr.PasswordRequired as ex:
            raise IOError("Password required for opening archive") from ex
        self._archive = None

    @property
    def closed(self):
        return True if self._archive is None else self._archive.fp.closed

    def _write_metadata(self, archive):
        archive.writestr(self.metadata.json(indent=2), arcname=AIPackage.METADATA_URI)

    def open_read(self):
        if self._archive is None:
            try:
                self._archive = py7zr.SevenZipFile(self.path, "r", password=self.password)
            except py7zr.Bad7zFile as ex:
                raise IOError(MSG_OPEN_ERROR) from ex
        if self._archive.mode != "r":
            raise IOError("Archive already opened in write mode")
        return self

    def open_write(self):
        if self._archive is None:
            try:
                self._archive = py7zr.SevenZipFile(self.path, "w", password=self.password)
            except py7zr.Bad7zFile as ex:
                raise IOError(MSG_OPEN_ERROR) from ex
            self.metadata.assets.clear()
        if self._archive.mode != "w":
            raise IOError("Archive already opened in read mode")
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._archive.mode == "w":
            self._write_metadata(self._archive)
        self._archive.close()
        self._archive = None

    def get_asset(self, name, validate=True):
        if self._archive is None:
            raise IOError("Archive not open. use: 'with archive.open_read() as reader:'")
        if self._archive.mode != "r":
            raise IOError("Archive not in read mode. use: 'with archive.open_read() as reader:'")
        try:
            asset = self.metadata.assets[name]
        except KeyError as ex:
            raise KeyError(f"Asset '{name} not in archive'") from ex

        try:
            data = self._archive.read(targets=asset.file)[asset.file]
            self._archive.reset()
            if validate and self._get_hash(data) != asset.hash:
                raise IOError("Asset file does not match asset hash")
            return data
        except py7zr.Bad7zFile as ex:
            raise IOError("Error extracting asset from archive") from ex

    def add_asset(self, name, arcname, file) -> AIPackageAsset:
        """
        Add an asset to the archive

        Args:
            name: name of asset
            arcname: name of file location in archive to save asset
            file: Path to asset to add to archive

        Returns:
            ModelArchiveAsset
        """
        if self._archive is None:
            raise IOError("Archive not open. use: 'with archive.open_write() as writer:'")
        if self._archive.mode != "w":
            raise IOError("Archive not in write mode. use: 'with archive.open_write() as writer:'")

        # Normalize path
        arcname = os.path.normpath(arcname).replace("\\", "/")

        # Create asset
        asset = AIPackageAsset(file=arcname, hash=self._get_hash(file))
        self._archive.write(file, arcname=arcname)
        self.metadata.assets[name] = asset
        return asset

    @staticmethod
    def _get_hash(data):
        sha256 = hashlib.sha256()
        if isinstance(data, BytesIO):
            for byte_block in iter(lambda: data.read(4096), b""):
                sha256.update(byte_block)
            data.seek(0)
        else:
            with open(data, "rb") as fp:
                # Read and update hash string value in blocks of 4K
                for byte_block in iter(lambda: fp.read(4096), b""):
                    sha256.update(byte_block)

        return f"sha256:{sha256.hexdigest()}"

    @property
    def versioned_name(self) -> str:
        """
        Get a versioned name according to the specification name.tar.gz -> name.version.tar.gz
        where the version is generated by `get_model_version`

        Returns: versioned file name

        """
        if not os.path.isfile(self.path):
            raise IOError("Archive does not exist, use 'with' keyword build archive")
        if not self.closed:
            raise IOError("Archive file not closed")

        archive_name = os.path.basename(self.path)
        split_name = archive_name.rsplit(".", 1)
        split_name.insert(1, str(get_model_version(self.path)))
        return ".".join(split_name)

    @classmethod
    def from_job(cls, job, tmpdir):
        if not job.model_path:
            raise AttributeError("Job does not contain an AiPackage")
        model_archive_path = job.job_dir / job.model_path
        tmp_archive_path = AnyPath(tmpdir) / model_archive_path.name
        shutil.copy(model_archive_path, tmp_archive_path)
        return cls(path=tmp_archive_path)
