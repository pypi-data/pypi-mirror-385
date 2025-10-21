import json
import os
import math
from collections.abc import Iterable
import itertools
from typing import List, Union
import warnings

import cv2
import numpy as np
from tqdm import tqdm

from brevettiai.io import AnyPath
from brevettiai.io.files import load_files


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "numpy"):
            return obj.numpy().tolist()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return obj.decode()
        elif isinstance(obj, np.generic):
            return obj.item()
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)


def _tile2d(x, grid=(10, 10)):
    generator = itertools.chain(x, itertools.repeat(np.zeros_like(x[0])))
    return np.vstack([np.hstack(list(itertools.islice(generator, int(grid[1])))) for _ in range(int(grid[0]))])


def create_atlas_v1(dataset, count=None):
    import tensorflow as tf

    ds = dataset.get_dataset()
    if isinstance(ds.element_spec, Iterable):
        ds = ds.map(lambda x, *_: x)
    if len(ds.element_spec.shape) > 3:
        ds = ds.unbatch()
    ds = ds.map(lambda x: tf.cast(x, np.uint8))
    if count:
        ds = ds.take(count)

    images = np.squeeze(np.stack(list(tqdm(ds.as_numpy_iterator(), total=count))))

    atlas_size = int(math.ceil(math.sqrt(len(images))))
    atlas = _tile2d(images, (atlas_size, atlas_size))
    return atlas


def build_facets(dataset, facet_dive, facet_sprite=None, count=4096, exclude_rows=None):
    warnings.warn('This is deprecated', DeprecationWarning, stacklevel=2)
    build_facets_from_dataset(dataset, facet_dive, facet_sprite, count, exclude_rows)


def build_facets_from_dataset(dataset, facet_dive, facet_sprite=None, count=4096, exclude_rows=None):
    """
    Build facets files
    :param dataset:
    :param facet_dive: path to facets dive json file or facets dive folder path
    :param facet_sprite: path to facets image sprite path
    :param count: max count of items
    :param exclude_rows: exclude named rows from dataset
    :return:
    """
    from brevettiai.io import io_tools
    exclude_rows = exclude_rows if exclude_rows is not None else {"path", "bucket"}
    facet_dive = AnyPath(facet_dive)
    if facet_sprite is None:
        facet_dir = facet_dive
        facet_dive = facet_dir / "facets.json"
        facet_sprite = facet_dir / "spriteatlas.jpeg"
    else:
        facet_sprite = AnyPath(facet_sprite)

    samples = itertools.islice(dataset.get_samples_numpy(batch=False), count)
    facet_data = [{k: v for k, v in sample.items() if k not in exclude_rows} for sample in samples]
    facet_dive.write_text(JsonEncoder().encode(facet_data))

    atlas = create_atlas_v1(dataset, count)
    if atlas.ndim == 3 and atlas.shape[2] >= 3:
        atlas = atlas[:, :, :-4:-1]  # Convert back to bgr format cv2.cvtColor(, cv2.COLOR_BGR2RGB)
    jpeg_created, buffer = cv2.imencode(".jpeg", atlas)
    assert jpeg_created
    facet_sprite.write_bytes(bytes(buffer))
    return True


def _make_thumbnail(_, content):
    img = cv2.imdecode(np.frombuffer(content, np.uint8), -1)
    return cv2.resize(img, (64, 64), interpolation=cv2.INTER_AREA)


def create_atlas(sprites, verbose=True):
    """Create atlas jpeg buffer from list of sprites or paths"""
    is_bgr = False
    if hasattr(sprites, "to_list"):
        sprites = sprites.to_list()

    if type(sprites[0]) == str or isinstance(sprites[0], os.PathLike):
        sprites = list(load_files(
            paths=sprites, callback=_make_thumbnail, monitor=verbose,
            tqdm_args=dict(desc="Loading images for facets atlas", total=len(sprites))
        ))
        is_bgr = True

    atlas_size = int(math.ceil(math.sqrt(len(sprites))))
    atlas = _tile2d(sprites, (atlas_size, atlas_size))

    # Convert to BGR
    if not is_bgr and atlas.ndim == 3 and atlas.shape[2] >= 3:
        atlas = atlas[:, :, :-4:-1]

    jpeg_created, buffer = cv2.imencode(".jpeg", atlas)
    if not jpeg_created:
        raise ValueError("Could not encode atlas to jpeg")
    return bytes(buffer)


def export_facets(path, info, sprites: List[Union[str, np.ndarray]]):
    """
    Create and export facets data to directory
    :param path: location to put the facets.json and spriteatlas.jpeg
    :param info: dataframe containing all the information about the samples
    :param sprites: list of strings or sprites to be used in the atlas. Sprites must be 64x64px
    :param io: io_module to write data
    :return:
    """
    if type(path) == str:
        path = AnyPath(path)

    info = JsonEncoder().encode(info.to_dict(orient="records"))
    (path / "facets.json").write_text(info)

    atlas = create_atlas(sprites)
    (path / "spriteatlas.jpeg").write_bytes(atlas)
