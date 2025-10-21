import pydantic.color as pydantic_color
from typing import Union, Tuple

try:
    import mmh3
    _hashfn = mmh3.hash
except ImportError:
    _hashfn = hash

COLOR_SCHEME = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099", "#0099c6", "#dd4477", "#66aa00", "#b82e2e",
                "#316395", "#994499", "#22aa99", "#aaaa11", "#6633cc", "#e67300", "#8b0707", "#651067", "#329262",
                "#5574a6", "#3b3eac"]


def get_color(v):
    """Get color from color scheme based on object"""
    if type(v) != int:
        v = _hashfn(v)
    return COLOR_SCHEME[v % len(COLOR_SCHEME)]


class Color(pydantic_color.Color):
    def __init__(self, value: Union[pydantic_color.ColorType, Tuple]) -> None:
        if isinstance(value, str):
            value = value.replace("hsla", "hsl")
        super().__init__(value)

    @classmethod
    def from_hsl(cls, h, s, l, a=None):
        r, g, b = pydantic_color.hls_to_rgb(h, l, s)
        return cls((255 * r, 255 * g, 255 * b, a))
