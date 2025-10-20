import itertools
import unittest

import matplotlib.pyplot as plt
import numpy as onp
from parameterized import parameterized

from ccmaps import ccmaps


class CustomCmapTest(unittest.TestCase):
    def test_wbgyr(self):
        plt.imshow(onp.ones((10, 10)), cmap=ccmaps.WBGYR)

    def test_wbgyr_callable(self):
        cmap = ccmaps.wbgyr()
        plt.imshow(onp.ones((10, 10)), cmap=cmap)

    def test_bkr(self):
        plt.imshow(onp.ones((10, 10)), cmap=ccmaps.BKR)

    def test_bkr_callable(self):
        cmap = ccmaps.bkr()
        plt.imshow(onp.ones((10, 10)), cmap=cmap)

    @parameterized.expand(
        itertools.product(
            [450.0, 550.0, 650.0],
            ("k", "w", (0.5, 0.5, 0.5)),
        )
    )
    def test_wavelength(self, wavelength_nm, background_color):
        cmap = ccmaps.cmap_for_wavelength(
            wavelength_nm=wavelength_nm,
            background_color=background_color,
        )
        plt.imshow(onp.ones((10, 10)), cmap=cmap)
