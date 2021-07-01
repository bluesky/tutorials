import os

import numpy as np


class NpyHandler:
    """
    Class to deal with reading npy files

    Parameters
    ----------
    fpath : str
        Path to file

    mmap_mode : {'r', 'r+', c}, optional
        memmap mode to use to open file
    """

    specs = {"npy"}

    def __init__(self, filename, mmap_mode=None):
        self._mmap_mode = mmap_mode
        if not os.path.exists(filename):
            raise IOError("the requested file {fpath} does not exist")
        self._fpath = filename

    def __call__(self):
        return np.load(self._fpath, self._mmap_mode)

    def get_file_list(self, datum_kwarg_gen):
        return [self._fpath]


class NpyFrameWise:
    specs = {"npy_FRAMEWISE"}

    def __init__(self, filename, mmap_mode=None):
        self._mmap_mode = mmap_mode
        if not os.path.exists(filename):
            raise IOError("the requested file {fpath} does not exist")
        self._fpath = filename
        self._data = np.load(self._fpath, self._mmap_mode)

    def __call__(self, frame_no):
        return self._data[frame_no]

    def get_file_list(self, datum_kwarg_gen):
        return [self._fpath]
