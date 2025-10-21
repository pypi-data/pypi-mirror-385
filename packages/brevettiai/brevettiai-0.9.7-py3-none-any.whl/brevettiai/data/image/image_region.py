import numpy as np

from typing import NamedTuple
from pydantic import BaseModel, Field
import warnings

warnings.warn('Deprecated, to be removed in a future release', DeprecationWarning, stacklevel=2)


class Point(NamedTuple):
    """
    Point as (y, x)

    y: Height (row)
    x: Width (column)
    """
    y: int
    x: int


class ImageRegion(BaseModel):
    """
    Region of an image specified by Origin, height and width
    """
    origin: Point = Field(description="origin of image region, as (row, column)")
    height: int = Field(description="Height of image region", gt=0)
    width: int = Field(description="Width of image region", gt=0)

    def bbox(self, divisible_by=1) -> 'BBOX':
        from brevettiai.data.tf_types import BBOX
        bbox = BBOX(
            y1=self.origin[0], x1=self.origin[1],
            y2=self.origin[0]+self.height-1, x2=self.origin[1]+self.width-1)

        if divisible_by > 1:
            excess = np.array(bbox.shape) % divisible_by
            pre = excess // 2
            post = -(pre + excess % 2)
            bbox = BBOX(
                int(bbox.y1 + pre[0]),
                int(bbox.x1 + pre[1]),
                int(bbox.y2 + post[0]),
                int(bbox.x2 + post[1])
            )
        return bbox