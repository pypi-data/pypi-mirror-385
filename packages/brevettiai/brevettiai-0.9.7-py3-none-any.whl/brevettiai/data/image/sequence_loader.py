import logging

import numpy as np
import tensorflow as tf

from pydantic import Field
from typing import ClassVar, Literal, Type

from brevettiai.io import AnyPath
from brevettiai.data.image.image_loader import ImageLoader, ImageKeys
from brevettiai.data.tf_types import TfRange, BBOX, SequenceShape

log = logging.getLogger(__name__)


class SequenceLoaderV2(ImageLoader):
    type: Literal["BcimgDatasetSequenceLoaderV2"] = "BcimgDatasetSequenceLoaderV2"
    stack_channels: bool = True
    path_key: str = Field(default="paths", exclude=True)
    range_meta: ClassVar[Type] = TfRange
    shape_meta: ClassVar[Type] = SequenceShape
    metadata_spec = {
        "sequence_shape": SequenceShape.build,
        ImageKeys.BOUNDING_BOX: BBOX.build,
    }

    def load(self, paths, metadata=None, postprocess=True, **kwargs):
        shape = metadata["sequence_shape"]

        default_shape = (shape.height, shape.width, shape.channels if self.channels == 0 else self.channels)
        if metadata is not None:
            if ImageKeys.BOUNDING_BOX in metadata:
                default_shape = (*metadata[ImageKeys.BOUNDING_BOX].shape, default_shape[-1])

        if self.postprocessor and postprocess:
            default_shape = (*self.postprocessor.output_size(default_shape[0], default_shape[1]),
                             self.postprocessor.output_channels(default_shape[2]))

        images, meta = tf.map_fn(
            fn=lambda x: super(SequenceLoaderV2, self).load(x, metadata, postprocess=postprocess,
                                                          default_shape=default_shape),
            elems=paths if tf.is_tensor(paths) else np.array(paths),
            fn_output_signature=(tf.float32, {'_image_file_shape': tf.int32}),
            parallel_iterations=16
        )
        if self.stack_channels:
            images = tf.transpose(images, [1, 2, 0, 3])
            sh = tf.shape(images)
            images = tf.reshape(images, [sh[0], sh[1], sh[2] * sh[3]])

        _image_file_shape = meta["_image_file_shape"][0]

        return images, {"_image_file_shape": _image_file_shape}


class SequenceLoader(ImageLoader):
    type: Literal["BcimgDatasetSequenceLoader"] = "BcimgDatasetSequenceLoader"
    stack_channels: bool = True
    path_key: str = Field(default="path_format", exclude=True)
    range_meta: ClassVar[Type] = TfRange
    shape_meta: ClassVar[Type] = SequenceShape
    metadata_spec = {
        "bucket": lambda x: x,
        "sequence_shape": SequenceShape.build,
        ImageKeys.BOUNDING_BOX: BBOX.build,
        ImageKeys.SEQUENCE_RANGE: range_meta.build,
    }

    def load_sequence(self, bucket, path_format, frames):
        if hasattr(bucket, "item"):
            bucket = bucket.item()
            path_format = path_format.item()
        if type(bucket) == bytes:
            bucket = bucket.decode()
            path_format = path_format.decode()
        bucket = AnyPath(bucket)
        sequence_files = np.array([str(bucket / path_format.format(frame=i)) for i in range(frames)])
        return sequence_files

    def load(self, path_format, metadata=None, postprocess=True, **kwargs):
        bucket = metadata["bucket"]
        shape = metadata["sequence_shape"]
        files = tf.numpy_function(self.load_sequence, [bucket, path_format, shape.frames], tf.string,
                                  name="format_files")

        default_shape = (shape.height, shape.width, shape.channels if self.channels == 0 else self.channels)
        if metadata is not None:
            # Select frames
            if ImageKeys.SEQUENCE_RANGE in metadata:
                files = metadata[ImageKeys.SEQUENCE_RANGE].slice_padded(files, "")
            if ImageKeys.BOUNDING_BOX in metadata:
                default_shape = (*metadata[ImageKeys.BOUNDING_BOX].shape, default_shape[-1])

        if self.postprocessor and postprocess:
            default_shape = (*self.postprocessor.output_size(default_shape[0], default_shape[1]),
                             self.postprocessor.output_channels(default_shape[2]))

        images, meta = tf.map_fn(
            fn=lambda x: super(SequenceLoader, self).load(x, metadata, postprocess=postprocess,
                                                          default_shape=default_shape),
            elems=files,
            fn_output_signature=(tf.float32, {'_image_file_shape': tf.int32}),
            parallel_iterations=16
        )
        if self.stack_channels:
            images = tf.transpose(images, [1, 2, 0, 3])
            sh = tf.shape(images)
            images = tf.reshape(images, [sh[0], sh[1], sh[2] * sh[3]])

        _image_file_shape = meta["_image_file_shape"][0]

        return images, {"_image_file_shape": _image_file_shape, "_sequence_files": files}


@tf.function
def format_frames(fmt, frames):
    a = tf.strings.split(fmt, "{frame")
    # If no frame marker is in format
    if tf.shape(a) != 2:
        return fmt[None]
    b = tf.strings.split(a[1], "}")

    frame_str = tf.strings.as_string(frames)
    # If fill is specified
    if tf.strings.substr(b[0], 0, 1) == ":":
        width = tf.strings.to_number(tf.strings.substr(b[0], 2, 1), tf.int32)
        frame_strings = []
        for fs in frame_str:
            # fill = tf.strings.reduce_join(tf.repeat("0", width - tf.strings.length(fs)))
            # filled_string = fill
            frame_strings.append(fs)
        frame_str = tf.convert_to_tensor(frame_strings)
    files = a[0] + frame_str + b[1]
    return files
