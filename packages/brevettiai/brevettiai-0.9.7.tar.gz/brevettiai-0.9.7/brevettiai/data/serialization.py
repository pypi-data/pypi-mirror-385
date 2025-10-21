import numpy as np

flag_order = 2**np.hstack([np.array([0, 8, 16]) + x for x in reversed(range(8))] + list(range(24, 32)))


def make_png_able(arr, channel_encoding=None):
    """Encode a 3/4 dimensional boolean image into an 8-bit RGBA array to save as png"""
    if channel_encoding is None:
        channel_encoding = flag_order
    if arr.ndim != 3 and arr.ndim != 3:
        raise ValueError("Array must have 3 dimensions")
    channels = arr.shape[-1]
    flags = (np.tensordot(arr.astype(bool), channel_encoding[:channels], 1) + (channels <= 24) * 0xFF000000).astype(np.uint32)
    flag_bytes = flags.view(np.dtype((np.uint8, 4)))
    return flag_bytes


def from_png_able_array(arr, channels=0, channel_encoding=None):
    """Decode a 8-bit RGBA image (batch of images) into a boolean 3 dimensional mask"""
    if channel_encoding is None:
        channel_encoding = flag_order
    if channels == 0:
        channels = len(channel_encoding)
    flags = arr.view(np.uint32)[..., 0]
    return (flags[..., None] & channel_encoding[None, None, :channels]).astype(bool)
