from scipy import ndimage
import numpy as np


def simple_integration(image, num_bins=3001):
    sx, sy = image.shape
    x_, y_ = np.mgrid[-sx // 2 : sx // 2, -sy // 2 : sy // 2]
    r = np.hypot(x_, y_)
    rbin = (num_bins * r / r.max()).astype(np.int)
    radial_mean = ndimage.mean(image, labels=rbin, index=np.arange(1, rbin.max() + 1))
    return radial_mean
