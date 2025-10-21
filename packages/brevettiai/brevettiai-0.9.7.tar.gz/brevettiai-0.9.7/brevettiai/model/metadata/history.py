from datetime import datetime
from typing import Optional, List, Union, Dict
from uuid import uuid4

from pydantic import BaseModel, root_validator, Field, Extra

from brevettiai.platform.models.job import JobOutput, Job


class ModelHistoryItem(BaseModel):
    """Base class for model history items"""
    type: Optional[str] = Field(default=None, description="Object specifier")
    history_item_version: str = Field(default="1.0", description="Metadata version number marker")
    history_item_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H%M%S"))
    source_model_id: str

    @root_validator(pre=True)
    def get_type(cls, values):
        # Set type if not given to ensure it is set
        if "type" not in values or values["type"] is None:
            values["type"] = cls.__name__
        return values

    class Config:
        extra = Extra.allow


class JobHistoryItem(ModelHistoryItem):
    job: JobOutput

    @classmethod
    def from_job(cls, source_model_id: str, job: Job):
        return cls(source_model_id=source_model_id, timestamp=job.run_id, job=job.job_output)


KnownHistoryItems = Union[JobHistoryItem, ModelHistoryItem, Dict]


class ModelHistory(BaseModel):
    __root__: List[KnownHistoryItems] = Field(default_factory=list)

    def append(self, item: ModelHistoryItem):
        self.__root__.append(item)
        return self

    def __getitem__(self, index):
        return self.__root__[index]

    def __len__(self):
        return len(self.__root__)
