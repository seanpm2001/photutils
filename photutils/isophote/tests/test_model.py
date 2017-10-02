# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pytest

from astropy.io import fits
from astropy.tests.helper import remote_data

from .make_test_data import make_test_image
from ..ellipse import Ellipse
from ..geometry import Geometry
from ..model import build_model
from ...datasets import get_path

try:
    import scipy
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@remote_data
@pytest.mark.skipif('not HAS_SCIPY')
def test_model(verbose=False):
    path = get_path('isophote/M105-S001-RGB.fits',
                    location='photutils-datasets', cache=True)
    hdu = fits.open(path)
    data = hdu[0].data[0]
    hdu.close()

    g = Geometry(530., 511, 10., 0.1, 10./180.*np.pi)
    ellipse = Ellipse(data, geometry=g, verbose=verbose, threshold=1.e5)
    isophote_list = ellipse.fit_image(verbose=verbose)
    model = build_model(data, isophote_list,
                        fill=np.mean(data[10:100, 10:100]), verbose=verbose)

    assert data.shape == model.shape

    residual = data - model
    assert np.mean(residual) <= 5.0
    assert np.mean(residual) >= -5.0


@pytest.mark.skipif('not HAS_SCIPY')
def test_model_simulated_data(verbose=False):
    data = make_test_image(eps=0.5, pa=np.pi/3., noise=1.e-2,
                           random_state=123)

    g = Geometry(256., 256., 10., 0.5, np.pi/3.)
    ellipse = Ellipse(data, geometry=g, verbose=verbose, threshold=1.e5)
    isophote_list = ellipse.fit_image(verbose=verbose)
    model = build_model(data, isophote_list,
                        fill=np.mean(data[0:50, 0:50]), verbose=verbose)

    assert data.shape == model.shape

    residual = data - model
    assert np.mean(residual) <= 5.0
    assert np.mean(residual) >= -5.0
