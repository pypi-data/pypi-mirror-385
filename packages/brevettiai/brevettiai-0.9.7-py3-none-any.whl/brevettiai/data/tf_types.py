"""
Classes which are serializable to tuples to allow use in tensorflow datasets
"""
from dataclasses import dataclass

import numpy as np
import warnings

warnings.warn('Deprecated, to be removed in a future release', DeprecationWarning, stacklevel=2)

try:
    import tensorflow as tf
except ImportError:
    pass


@dataclass(frozen=True, order=True)
class TfRange:
    """
    An object for slicing tensors
    """
    start: int = 0
    "Index of start frame"
    end: int = 0
    "Index of frame after last frame in sequence"

    def slice(self, sequence):
        if self.end == 0:
            return sequence[tf.cast(self.start, tf.int32):]
        else:
            return sequence[tf.cast(self.start, tf.int32):tf.cast(self.end, tf.int32)]

    def slice_padded(self, sequence, constant_value):
        start = tf.cast(self.start, tf.int32)
        end = tf.cast(self.end, tf.int32)
        if end <= 0:
            end = tf.shape(sequence)[0] + end
        pad_start = -tf.minimum(start, 0)
        length = tf.shape(sequence)[0]
        pad_end = tf.maximum(end-length, 0)
        sequence = tf.pad(sequence, [(pad_start, pad_end)], constant_values=constant_value)

        return sequence[start + pad_start: end + pad_start]

    def frames(self):
        return tf.range(self.start, self.end)

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


@dataclass(frozen=True, order=True)
class BBOX:
    """
    An object for slicing images according to bounding boxes

    y1: vertical offset
    x1: horizontal offset
    y2: End vertical offset (included)
    x2: End horizontal offset (included)
    """
    y1: int = 0
    """vertical offset"""
    x1: int = 0
    """horizontal offset"""
    y2: int = 0
    """End vertical offset (included)"""
    x2: int = 0
    """End horizontal offset (included)"""

    @property
    def empty(self):
        return tf.reduce_all(tf.equal(tuple(self), 0))

    @property
    def valid(self):
        return tf.reduce_all(tf.greater(self.shape, 0))

    def slice(self, image, offset_y=0, offset_x=0, zoom=1):
        shy, shx = self.shape
        y1 = (self.y1 + offset_y) // zoom
        y2 = y1 + shy // zoom
        x1 = (self.x1 + offset_x) // zoom
        x2 = x1 + shx // zoom
        return image[y1:y2, x1:x2]

    @property
    def shape(self):
        """
        Get shape of the bounding box

        Returns:
            height, width
        """
        return self.y2 - self.y1 + 1, self.x2 - self.x1 + 1

    @property
    def area(self):
        """
        Get area of bounding box

        Returns:

        """
        return tf.reduce_prod(self.shape)
        #return np.prod(self.shape)

    @classmethod
    def build(cls, x):
        if isinstance(x, cls):
            return x
        return cls(x[0], x[1], x[2], x[3])

    @classmethod
    def from_shape(cls, height, width):
        return cls(0, 0, height - 1, width - 1)

    def numpy(self):
        return np.array(tuple(self))

    def scale(self, scale):
        """
        Scale bounding box

        Args:
            scale: scaling factor to multiply the coordinates with

        Returns:

        """
        return BBOX(int(scale * float(self.y1)), int(scale * float(self.x1)),
                    int(np.floor(scale * float(self.y2))), int(np.floor(scale * float(self.x2))))

    def union(self, other):
        return BBOX(min(self.y1, other.y1), min(self.x1, other.x1), max(self.y2, other.y2), max(self.x2, other.x2))

    def intersection(self, other):
        return BBOX(max(self.y1, other.y1), max(self.x1, other.x1), min(self.y2, other.y2), min(self.x2, other.x2))

    def __iter__(self):
        yield from (self.y1, self.x1, self.y2, self.x2)

    def __str__(self):
        return f"BBOX(y1={int(self.y1)}, x1={int(self.x1)}, y2={int(self.y2)}, x2={int(self.x2)})"


@dataclass(frozen=True, order=True)
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
