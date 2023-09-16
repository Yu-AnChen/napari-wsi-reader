"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/guides.html?#readers
"""
from typing import Callable, List, Optional, Sequence, Union
import pathlib

import numpy as np
import palom.reader
from napari.types import LayerData

PathLike = str | pathlib.Path
PathOrPaths = Union[PathLike, Sequence[PathLike]]
ReaderFunction = Callable[[PathOrPaths], List[LayerData]]


def _is_ome_tiff(path):
    path = pathlib.Path(path)
    return ''.join(path.suffixes[-2:]) in ['.ome.tiff', '.ome.tif']


def _is_ashlar_lt_zarr(path):
    path = pathlib.Path(path)
    return path.is_dir() & path.name.endswith('-ashlar-lt.zarr')


def napari_get_reader(path: PathOrPaths) -> Optional[ReaderFunction]:
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str | pathlib.Path or list of (str | pathlib.Path)
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        for pp in path:
            pp = pathlib.Path(pp)
            if not (_is_ome_tiff(pp) | _is_ashlar_lt_zarr(pp)):
                return None

    # if we know we cannot read the file, we immediately return None.
    else:
        if not (_is_ome_tiff(path) | _is_ashlar_lt_zarr(path)):
            return None

    # otherwise we return the *function* that can read ``path``.
    return palom_ome_pyramid_reader


def palom_ome_pyramid_reader(path):
    import dask.array as da
    import zarr

    if not isinstance(path, list):
        path = [path]
    
    readers = []
    pyramids = []
    for pp in path:
        if _is_ome_tiff(pp):
            reader = palom.reader.OmePyramidReader(pp)
            readers.append(reader)
            pyramids.append(reader.pyramid)
        elif _is_ashlar_lt_zarr(pp):
            store = zarr.open(pp, mode='r')
            pyramid = [
                da.array([da.from_zarr(aa) for aa in group.values()])
                for _, group in store.groups()
            ]
            pyramid[1] = pyramid[1].persist()
            pyramid[2] = pyramid[2].persist()
            readers.append(store)
            pyramids.append(pyramid)

    return [(pp, dict(visible=False, channel_axis=0)) for pp in pyramids]


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    # load all files into array
    arrays = [np.load(_path) for _path in paths]
    # stack arrays into single array
    data = np.squeeze(np.stack(arrays))

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {}

    layer_type = "image"  # optional, default is "image"
    return [(data, add_kwargs, layer_type)]
