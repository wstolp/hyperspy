# -*- coding: utf-8 -*-
# Copyright 2007-2021 The HyperSpy developers
#
# This file is part of  HyperSpy.
#
#  HyperSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  HyperSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  HyperSpy.  If not, see <http://www.gnu.org/licenses/>.
# Original file from scikits-images
# Modified by the HyperSpy developers to add _tv_denoise_1d


import numpy as np


def _tv_denoise_3d(im, weight=100, eps=2.e-4, keep_type=False, n_iter_max=200):
    """
    Perform total-variation denoising on 3-D arrays

    Parameters
    ----------
    im: ndarray
        3-D input data to be denoised

    weight: float, optional
        denoising weight. The greater ``weight``, the more denoising (at
        the expense of fidelity to ``input``)

    eps: float, optional
        relative difference of the value of the cost function that determines
        the stop criterion. The algorithm stops when:

            (E_(n-1) - E_n) < eps * E_0

    keep_type: bool, optional (False)
        whether the output has the same dtype as the input array.
        keep_type is False by default, and the dtype of the output is float

    n_iter_max: int, optional
        maximal number of iterations used for the optimization.

    Returns
    -------
    out: ndarray
        denoised array

    Notes
    -----
    Rudin, Osher and Fatemi algorithm

    Examples
    ---------
    First build synthetic noisy data

    >>> x, y, z = np.ogrid[0:40, 0:40, 0:40]
    >>> mask = (x -22)**2 + (y - 20)**2 + (z - 17)**2 < 8**2
    >>> mask = mask.astype(float)
    >>> mask += 0.2*np.random.randn(*mask.shape)
    >>> res = tv_denoise_3d(mask, weight=100)
    """
    im_type = im.dtype
    if im_type is not float:
        im = im.astype(float)
    px = np.zeros_like(im)
    py = np.zeros_like(im)
    pz = np.zeros_like(im)
    gx = np.zeros_like(im)
    gy = np.zeros_like(im)
    gz = np.zeros_like(im)
    i = 0
    while i < n_iter_max:
        d = - px - py - pz
        d[1:] += px[:-1]
        d[:, 1:] += py[:, :-1]
        d[:, :, 1:] += pz[:, :, :-1]

        out = im + d
        E = (d ** 2).sum()

        gx[:-1] = np.diff(out, axis=0)
        gy[:, :-1] = np.diff(out, axis=1)
        gz[:, :, :-1] = np.diff(out, axis=2)
        norm = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2)
        E += weight * norm.sum()
        norm *= 0.5 / weight
        norm += 1.
        px -= 1. / 6. * gx
        px /= norm
        py -= 1. / 6. * gy
        py /= norm
        pz -= 1 / 6. * gz
        pz /= norm
        E /= float(im.size)
        if i == 0:
            E_init = E
            E_previous = E
        else:
            if np.abs(E_previous - E) < eps * E_init:
                break
            else:
                E_previous = E
        i += 1
    if keep_type:
        return out.astype(im_type)
    else:
        return out


def _tv_denoise_2d(im, weight=50, eps=2.e-4, keep_type=False, n_iter_max=200):
    """
    Perform total-variation denoising

    Parameters
    ----------
    im: ndarray
        input data to be denoised

    weight: float, optional
        denoising weight. The greater ``weight``, the more denoising (at
        the expense of fidelity to ``input``)

    eps: float, optional
        relative difference of the value of the cost function that determines
        the stop criterion. The algorithm stops when:

            (E_(n-1) - E_n) < eps * E_0

    keep_type: bool, optional (False)
        whether the output has the same dtype as the input array.
        keep_type is False by default, and the dtype of the output is float

    n_iter_max: int, optional
        maximal number of iterations used for the optimization.

    Returns
    -------
    out: ndarray
        denoised array

    Notes
    -----
    The principle of total variation denoising is explained in
    http://en.wikipedia.org/wiki/Total_variation_denoising

    This code is an implementation of the algorithm of Rudin, Fatemi and Osher
    that was proposed by Chambolle in [*]_.

    References
    ----------

    .. [*] A. Chambolle, An algorithm for total variation minimization and
           applications, Journal of Mathematical Imaging and Vision,
           Springer, 2004, 20, 89-97.

    Examples
    ---------
    >>> import scipy
    >>> ascent = scipy.ascent().astype(float)
    >>> ascent += 0.5 * ascent.std()*np.random.randn(*ascent.shape)
    >>> denoised_ascent = tv_denoise(ascent, weight=60.0)
    """
    im_type = im.dtype
    if im_type is not float:
        im = im.astype(float)
    px = np.zeros_like(im)
    py = np.zeros_like(im)
    gx = np.zeros_like(im)
    gy = np.zeros_like(im)
    d = np.zeros_like(im)
    i = 0
    while i < n_iter_max:
        d = -px - py
        d[1:] += px[:-1]
        d[:, 1:] += py[:, :-1]

        out = im + d
        E = (d ** 2).sum()
        gx[:-1] = np.diff(out, axis=0)
        gy[:, :-1] = np.diff(out, axis=1)
        norm = np.sqrt(gx ** 2 + gy ** 2)
        E += weight * norm.sum()
        norm *= 0.5 / weight
        norm += 1
        px -= 0.25 * gx
        px /= norm
        py -= 0.25 * gy
        py /= norm
        E /= float(im.size)
        if i == 0:
            E_init = E
            E_previous = E
        else:
            if np.abs(E_previous - E) < eps * E_init:
                break
            else:
                E_previous = E
        i += 1
    if keep_type:
        return out.astype(im_type)
    else:
        return out


def _tv_denoise_1d(im, weight=50, eps=2.e-4, keep_type=False, n_iter_max=200):
    """
    Perform total-variation denoising

    Parameters
    ----------
    im: ndarray
        input data to be denoised

    weight: float, optional
        denoising weight. The greater ``weight``, the more denoising (at
        the expense of fidelity to ``input``)

    eps: float, optional
        relative difference of the value of the cost function that determines
        the stop criterion. The algorithm stops when:

            (E_(n-1) - E_n) < eps * E_0

    keep_type: bool, optional (False)
        whether the output has the same dtype as the input array.
        keep_type is False by default, and the dtype of the output is float

    n_iter_max: int, optional
        maximal number of iterations used for the optimization.

    Returns
    -------
    out: ndarray
        denoised array

    Notes
    -----
    The principle of total variation denoising is explained in
    http://en.wikipedia.org/wiki/Total_variation_denoising

    This code is an implementation of the algorithm of Rudin, Fatemi and Osher
    that was proposed by Chambolle in [*]_.

    References
    ----------

    .. [*] A. Chambolle, An algorithm for total variation minimization and
           applications, Journal of Mathematical Imaging and Vision,
           Springer, 2004, 20, 89-97.

    Examples
    ---------
    >>> import scipy
    >>> ascent = scipy.misc.ascent().astype(float)
    >>> ascent += 0.5 * ascent.std()*np.random.randn(*ascent.shape)
    >>> denoised_ascent = tv_denoise(ascent, weight=60.0)
    """
    im_type = im.dtype
    if im_type is not float:
        im = im.astype(float)
    px = np.zeros_like(im)
    gx = np.zeros_like(im)
    d = np.zeros_like(im)
    i = 0
    while i < n_iter_max:
        d = -px
        d[1:] += px[:-1]

        out = im + d
        E = (d ** 2).sum()
        gx[:-1] = np.diff(out)
        norm = np.abs(gx)
        E += weight * norm.sum()
        norm *= 0.5 / weight
        norm += 1
        px -= 0.25 * gx
        px /= norm
        E /= float(im.size)
        if i == 0:
            E_init = E
            E_previous = E
        else:
            if np.abs(E_previous - E) < eps * E_init:
                break
            else:
                E_previous = E
        i += 1
    if keep_type:
        return out.astype(im_type)
    else:
        return out


def tv_denoise(im, weight=50, eps=2.e-4, keep_type=False, n_iter_max=200):
    """
    Perform total-variation denoising on 2-d and 3-d images

    Parameters
    ----------
    im: ndarray (2d or 3d) of ints, uints or floats
        input data to be denoised. `im` can be of any numeric type,
        but it is cast into an ndarray of floats for the computation
        of the denoised image.

    weight: float, optional
        denoising weight. The greater ``weight``, the more denoising (at
        the expense of fidelity to ``input``)

    eps: float, optional
        relative difference of the value of the cost function that
        determines the stop criterion. The algorithm stops when:

            (E_(n-1) - E_n) < eps * E_0

    keep_type: bool, optional (False)
        whether the output has the same dtype as the input array.
        keep_type is False by default, and the dtype of the output is float

    n_iter_max: int, optional
        maximal number of iterations used for the optimization.

    Returns
    -------
    out: ndarray
        Denoised array

    Notes
    -----
    The principle of total variation denoising is explained in
    http://en.wikipedia.org/wiki/Total_variation_denoising

    The principle of total variation denoising is to minimize the
    total variation of the image, which can be roughly described as
    the integral of the norm of the image gradient. Total variation
    denoising tends to produce "cartoon-like" images, that is,
    piecewise-constant images.

    This code is an implementation of the algorithm of Rudin, Fatemi and Osher
    that was proposed by Chambolle in [*]_.

    References
    ----------

    .. [*] A. Chambolle, An algorithm for total variation minimization and
           applications, Journal of Mathematical Imaging and Vision,
           Springer, 2004, 20, 89-97.

    Examples
    ---------
    >>> # 2D example using ascent
    >>> import scipy
    >>> ascent = scipy.misc.ascent().astype(float)
    >>> ascent += 0.5 * ascent.std()*np.random.randn(*ascent.shape)
    >>> denoised_ascent = tv_denoise(ascent, weight=60)
    >>> # 3D example on synthetic data
    >>> x, y, z = np.ogrid[0:40, 0:40, 0:40]
    >>> mask = (x -22)**2 + (y - 20)**2 + (z - 17)**2 < 8**2
    >>> mask = mask.astype(float)
    >>> mask += 0.2*np.random.randn(*mask.shape)
    >>> res = tv_denoise_3d(mask, weight=100)
    """

    if im.ndim == 2:
        return _tv_denoise_2d(im, weight, eps, keep_type, n_iter_max)
    elif im.ndim == 3:
        return _tv_denoise_3d(im, weight, eps, keep_type, n_iter_max)
    else:
        raise ValueError(
            'only 2-d and 3-d images may be denoised with this function')
