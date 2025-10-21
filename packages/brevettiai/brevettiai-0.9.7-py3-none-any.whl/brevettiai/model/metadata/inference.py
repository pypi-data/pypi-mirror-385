from typing import Literal, List, Optional
from pydantic import Field

from brevettiai.model import ModelMetadata
from brevettiai.data.image.image_region import ImageRegion


class InferenceModelMetadata(ModelMetadata):
    type: Optional[Literal["InferenceModelMetadata"]] = Field(default=None, description="Object specifier")
    version: str = Field(default="1.0", const=True, description="Metadata version number marker")

    input_type: Literal["greyscale", "rgb", "motionRGB"]
    roi: Optional[ImageRegion]
    classes: List[str]
