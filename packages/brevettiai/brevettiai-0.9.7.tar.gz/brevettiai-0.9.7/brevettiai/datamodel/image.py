import numpy as np

from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class ImageRegion:
    y: int
    x: int
    height: int
    width: int

    @classmethod
    def from_bbox(cls, obj):
        shape = obj.shape
        return cls(
            y=int(obj.y1),
            x=int(obj.x1),
            height=int(shape[0]),
            width=int(shape[1]),
        )


@dataclass(frozen=True, eq=True, order=True)
class SequenceShape:
    frames: int = 0
    height: int = 0
    width: int = 0
    channels: int = 0

    @classmethod
    def build(cls, x):
        return cls(x[0], x[1], x[2], x[3])

    @property
    def bbox(self):
        return BBOX(0, 0, self.height-1, self.width-1)

    def __iter__(self):
        yield from (self.frames, self.height, self.width, self.channels)

    def __str__(self):
        return f"SequenceShape{list(self)}"


@dataclass(frozen=True, eq=True, order=True)
class BBOX:
    """
    An object for slicing images according to bounding boxes

    y1: vertical offset
    x1: horizontal offset
    y2: End vertical offset (included)
    x2: End horizontal offset (included)
    """
    y1: float = 0
    """vertical offset"""
    x1: float = 0
    """horizontal offset"""
    y2: float = 0
    """End vertical offset (included)"""
    x2: float = 0
    """End horizontal offset (included)"""

    @property
    def empty(self):
        return self.y2 == 0 and self.x2 == 0 and self.y1 == 0 and self.x1 == 0

    @property
    def valid(self):
        return self.y2 >= self.y1, self.x2 >= self.x1

    def slice(self, image, offset_y=0, offset_x=0, zoom=1):
        shy, shx = self.shape
        y1 = np.floor((self.y1 + offset_y) // zoom).astype(int)
        y2 = np.ceil(y1 + shy // zoom).astype(int)
        x1 = np.floor((self.x1 + offset_x) // zoom).astype(int)
        x2 = np.ceil(x1 + shx // zoom).astype(int)
        return image[y1:y2, x1:x2]

    @property
    def shape(self):
        """
        Get shape of the bounding box

        Returns:
            height, width
        """
        return np.ceil(self.y2) - np.floor(self.y1), np.ceil(self.x2) - np.floor(self.x1)

    @property
    def area(self):
        """
        Get area of bounding box

        Returns:

        """
        shy, shx = self.shape
        return shy * shx

    @classmethod
    def build(cls, x):
        if isinstance(x, cls):
            return x
        return cls(x[0], x[1], x[2], x[3])

    @classmethod
    def from_shape(cls, height, width):
        return cls(0, 0, height, width)

    def numpy(self):
        return np.array(tuple(self))

    def scale(self, scale):
        """
        Scale bounding box

        Args:
            scale: scaling factor to multiply the coordinates with

        Returns:

        """
        return BBOX(scale * self.y1, scale * self.x1,
                    scale * self.y2, scale * self.x2)

    def union(self, other):
        return BBOX(min(self.y1, other.y1), min(self.x1, other.x1), max(self.y2, other.y2), max(self.x2, other.x2))

    def intersection(self, other):
        return BBOX(max(self.y1, other.y1), max(self.x1, other.x1), min(self.y2, other.y2), min(self.x2, other.x2))

    def __iter__(self):
        yield from (self.y1, self.x1, self.y2, self.x2)

    def __str__(self):
        return f"BBOX(y1={int(self.y1)}, x1={int(self.x1)}, y2={int(self.y2)}, x2={int(self.x2)})"

    @classmethod
    def from_geometry(cls, geom):
        bounds = geom.bounds
        return cls(int(bounds[1]), int(bounds[0]), int(bounds[3]), int(bounds[2]))


@dataclass(frozen=True, eq=True, order=True)
class SequenceRange:
    """
    An object for slicing tensors
    """
    start: int = 0
    "Index of start frame"
    end: int = 0
    "Index of frame after last frame in sequence"

    def slice(self, sequence):
        if self.end == 0:
            return sequence[np.int32(self.start):]
        else:
            return sequence[np.int32(self.start):np.int32(self.end)]

    def slice_padded(self, sequence, constant_value=0):
        start = np.int32(self.start)
        end = np.int32(self.end)
        if end <= 0:
            end = np.shape(sequence)[0] + end
        pad_start = -np.min([start, 0])
        length = np.shape(sequence)[0]
        pad_end = np.max([end-length, 0])
        sequence = np.pad(sequence, [(pad_start, pad_end)], constant_values=constant_value)

        return sequence[start + pad_start: end + pad_start]

    def frames(self):
        return np.arange(self.start, self.end)

    @classmethod
    def build(cls, x):
        return cls(x[0], x[1])

    @classmethod
    def build_single_frame(cls, frame):
        frame = int(frame)
        return cls(frame, frame + 1)

    def __iter__(self):
        yield from (self.start, self.end)

    def __str__(self):
        return f"SequenceRange{self.start, None if self.end == 0 else self.end}"
