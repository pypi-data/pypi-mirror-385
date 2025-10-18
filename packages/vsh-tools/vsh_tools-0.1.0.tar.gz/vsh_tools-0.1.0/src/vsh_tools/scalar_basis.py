#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: scalar_basis.py
"""
Scalar Spherical Harmonics (SSH) projections on the sphere.
"""

from __future__ import annotations

import numpy as np
from numpy import sqrt, pi, sin, cos

__all__ = ["sca_sph_harm_proj", "real_sca_sph_harm_proj"]


def sca_sph_harm_proj(l_max: int, ra, dc):
    """
    Compute (complex) scalar spherical harmonics up to degree l_max
    at positions (ra, dec).

    Parameters
    ----------
    l_max : int
        Maximum degree (>= 1).
    ra, dc : array_like (radians)
        Right ascension and declination arrays of equal length.

    Returns
    -------
    Y_mat : complex ndarray, shape (l_max+1, l_max+1, N)
        Entries Y_mat[l, m, i] are the complex values for 0<=m<=l.
        Other entries remain zero.
    """
    try:
        l_max = int(l_max)
    except Exception as e:
        raise ValueError("l_max must be convertible to int.") from e
    if l_max < 1:
        raise ValueError("l_max must be >= 1.")

    ra = np.asarray(ra, dtype=float)
    dc = np.asarray(dc, dtype=float)
    if ra.shape != dc.shape:
        raise ValueError("ra and dc must have the same shape.")
    N = ra.size

    x = sin(dc)
    fac_pol = np.sqrt(np.clip(1.0 - x * x, 0.0, 1.0))  # guard near poles

    # Associated Legendre P_{l,m}(sin dec) via recurrences (B.4–B.7 analogue)
    P = np.zeros((l_max + 1, l_max + 1, N), dtype=float)
    Y = np.zeros((l_max + 1, l_max + 1, N), dtype=complex)

    P[0, 0, :] = 1.0
    for l in range(1, l_max + 1):
        for m in range(l, -1, -1):  # m = l..0
            if m == 0:
                # leave P[l,0] to be filled through the l-2 recursion branch
                continue
            if l == m:
                P[l, m, :] = fac_pol * (2 * m - 1) * P[m - 1, m - 1, :]
            elif l == m + 1:
                P[l, m, :] = (2 * m + 1) * x * P[m, m, :]
            else:
                P[l, m, :] = ((2 * l - 1) * x * P[l - 1, m, :] -
                              (l - 1 + m) * P[l - 2, m, :]) / (l - m)

    # Complex SSH values Y_{l,m}(ra,dc)
    # NOTE: This uses the same prefactor as in your VSH code.
    # If you want the standard scalar SH normalization, replace the line with:
    #   coef = (2*l + 1)/(4*pi) * factorial(l - m)/factorial(l + m)
    for l in range(1, l_max + 1):
        for m in range(0, l + 1):
            # matching your VSH-style factor
            coef = (2 * l + 1) / (l * (l + 1)) / (4 * pi)
            # factorial ratio simplified is fine but we keep this compact using numpy broadcasting:
            # use a stable form via logs if you push to high l; here we keep it simple:
            # factorial(l-m)/factorial(l+m) == prod_{k=1}^{m} (l-k+1)/(l+k)
            rat = 1.0
            if m:
                num = np.arange(l - m + 1, l + 1, dtype=float)
                den = np.arange(l + 1, l + m + 1, dtype=float)
                rat = np.prod(num / den)
            coef = (-1) ** m * sqrt(coef * rat)

            phase = np.cos(m * ra) + 1j * np.sin(m * ra)
            Y[l, m, :] = coef * P[l, m, :] * phase

    return Y


def real_sca_sph_harm_proj(l: int, m: int, Y_mat: np.ndarray):
    """
    Real-valued SSH for given (l, m) from complex Y_mat.

    Parameters
    ----------
    l, m : int
        Degree and order (0 <= m <= l).
    Y_mat : complex ndarray
        Output of `sca_sph_harm_proj`.

    Returns
    -------
    If m == 0:
        Y_r : float ndarray (real part)
    If m > 0:
        Y_r, Y_i : float ndarray
        Real-basis components: ( 2*Re(Y), -2*Im(Y) ), matching VSH real-basis usage.
    """
    if not (0 <= m <= l):
        raise ValueError("Require 0 <= m <= l.")
    Y = Y_mat[l, m, :]

    if m == 0:
        return np.real(Y)

    # real-basis pair (consistent with your VSH real conversion)
    Y_r = 2.0 * np.real(Y)
    Y_i = -2.0 * np.imag(Y)
    return Y_r, Y_i
