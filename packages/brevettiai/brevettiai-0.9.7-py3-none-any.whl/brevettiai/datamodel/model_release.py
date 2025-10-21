from datetime import datetime

from brevettiai.io import AnyPath
from brevettiai.datamodel.camelmodel import CamelModel
from typing import TYPE_CHECKING, Optional
from pydantic import Field
import requests
import hashlib
import logging
import base64

if TYPE_CHECKING:
    from brevettiai import PlatformAPI

log = logging.getLogger(__name__)


class ModelReleaseMetadata(CamelModel):
    type: Optional[str]


class BaseModelDescription(CamelModel):
    """
    BaseModelDescription is a data model class that represents the description of a model release.

    Attributes:
        release_id (Optional[str]): The unique identifier for the model release.
        model_family_id (Optional[str]): The unique identifier for the model family.
        model_family_name (Optional[str]): The name of the model family.
        version (Optional[int]): The version number of the model release.
    """

    release_id: Optional[str]
    model_family_id: Optional[str]
    model_family_name: Optional[str]
    version: Optional[int]


class ModelArtifact(CamelModel):
    download_url: str
    file_name: str
    sha256: str

    def download(
        self,
        dir: AnyPath,
        filename: str = None,
        job: None = None,
        client: "PlatformAPI" = None,
    ) -> str:
        path = dir / (filename or self.file_name)
        try:
            # Check if file already exists and has correct hash
            self.check_integrity(path)
            log.info(f"Reusing existing model artifact {path}")
            return path
        except (ValueError, FileNotFoundError):
            pass

        log.info(f"Downloading model artifact {self.file_name} to {dir}")
        dir.mkdir(parents=True, exist_ok=True)
        if job:
            r = requests.get(
                f"{job.host_name}{self.download_url}", auth=job.auth, stream=True
            )
            r.raise_for_status()

            # download file
            with path.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return path
        if client:
            return client.download_url(self.download_url, path)
        raise ValueError("Provide either job or client to download model release")

    def check_integrity(self, path: AnyPath):
        # calculate sha256 hash of file
        if not path.exists():
            raise FileNotFoundError(f"File {path} not found")

        sha256 = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        b64hash = base64.b64encode(sha256.digest()).decode()

        if b64hash != self.sha256:
            raise ValueError("File integrity check failed")


class ModelRelease(CamelModel):
    id: Optional[str] = Field(alias="releaseId")
    model_id: Optional[str] = Field(alias="modelId")
    model_name: Optional[str]
    model_family: Optional["ModelFamily"]
    metadata: Optional[ModelReleaseMetadata] = Field(alias="modelMetadata")
    version: Optional[int] = Field(alias="releaseVersion")
    created_at: Optional[datetime] = Field(alias="createdAt")
    published_at: Optional[datetime] = Field(alias="publishedAt")
    artifact: Optional[ModelArtifact]

    @classmethod
    def from_name(cls, client: "PlatformAPI", name: str, version: int):
        family = client.get_modelfamilies(name=name)
        family = family.populate(client)
        return family.version(version)

    def populate(self, client: "PlatformAPI") -> "ModelRelease":
        return client.get_modelrelease(self.model_id)

    def base_model_description(self):
        return BaseModelDescription(
            release_id=self.id,
        )


class ModelFamily(CamelModel):
    id: Optional[str]
    name: str
    description: Optional[str]
    organization: Optional["ModelFamily.OrganizationDescription"]

    members: Optional[list[ModelRelease]]

    class OrganizationDescription(CamelModel):
        id: str
        name: str

    def populate(self, client: "PlatformAPI") -> "ModelFamily":
        return client.get_modelfamilies(self.id)

    def released_members(self) -> list[ModelRelease]:
        return [entry for entry in self.members if entry.id is not None]

    def latest(self) -> ModelRelease:
        candidates = self.released_members()
        if not candidates:
            raise ValueError(f"No released entries in model family {self.name}")

        latest = candidates[0]
        for entry in candidates[1:]:
            if entry.version > latest.version:
                latest = entry
        return latest

    def version(self, version: int) -> ModelRelease:
        for entry in self.members:
            if entry.version == version:
                return entry
        raise ValueError(f"Version {version} not found in model family {self.name}")


class ReleaseMetadata(CamelModel):
    model_family: ModelFamily | str
    model_metadata: Optional[ModelReleaseMetadata]


ModelRelease.update_forward_refs()
