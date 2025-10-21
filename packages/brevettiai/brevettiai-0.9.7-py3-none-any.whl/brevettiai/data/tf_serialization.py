# Tensorflow compatible versions of serialization.py
import tensorflow as tf

from brevettiai.data.serialization import flag_order


@tf.function
def make_png_able(arr, channel_encoding=None):
    if channel_encoding is None:
        channel_encoding = flag_order
    tf.debugging.assert_rank(arr, 3)
    channels = arr.shape[-1]
    alpha_mask = (channels <= 24) * 0xFF000000
    flags = tf.tensordot(tf.cast(tf.cast(arr, bool), tf.int64), tf.cast(channel_encoding[:channels], tf.int64), 1) + alpha_mask
    flag_bytes = tf.bitcast(tf.cast(flags, tf.uint32), tf.uint8)
    return flag_bytes


@tf.function
def from_png_able_array(arr, channels=0, channel_encoding=None):
    if channel_encoding is None:
        channel_encoding = flag_order
    if channels == 0:
        channels = len(channel_encoding)
    flags = tf.bitcast(arr, tf.uint32)[..., None]
    return tf.cast(tf.cast(flags & channel_encoding[None, None, :channels], bool), tf.uint8)


@tf.function
def load_png_able_array(path, channel_encoding):
    buffer = tf.io.read_file(path)
    return from_png_able_array(tf.io.decode_png(buffer), channel_encoding=channel_encoding)


@tf.function
def write_png_able_array(path, arr):
    buffer = tf.io.encode_png(make_png_able(arr))
    tf.io.write_file(path, buffer)
    return arr
