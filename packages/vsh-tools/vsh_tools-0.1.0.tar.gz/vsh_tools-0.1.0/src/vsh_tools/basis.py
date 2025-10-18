#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: basis.py
"""
Vector Spherical Harmonics (VSH) basis projections.

Reference
---------
F. Mignard & S. Klioner, A&A 547, A59 (2012).
DOI: 10.1051/0004-6361/201219927.
"""

from __future__ import annotations

import numpy as np
from numpy import sqrt, pi, sin, cos
from math import factorial
from typing import Tuple

__all__ = ["vec_sph_harm_proj", "real_vec_sph_harm_proj"]

# -----------------------------  FUNCTIONS -----------------------------


def vec_sph_harm_proj(
    l_max: int,
    ra: np.ndarray,
    dc: np.ndarray,
    sph_type: str = "T",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute complex VSH projections T_lm (or S_lm) onto (e_ra, e_dec) at (ra, dec).

    Parameters
    ----------
    l_max : int
        Maximum degree of the harmonics (>= 1).
    ra, dc : array_like of float (radians)
        Right ascension and declination arrays of equal length.
    sph_type : {"T","S"}, optional
        Return toroidal ("T") or spheroidal ("S") projections. Default "T".

    Returns
    -------
    T_ra_mat, T_dc_mat : complex ndarray, shape (l_max+1, l_max+1, N)
        For each (l, m), the projection of the vector harmonic onto e_ra and e_dec.

    Notes
    -----
    - m runs 0..l; entries where 0 <= m <= l are filled, others remain zero.
    - S_lm is obtained from T_lm via (S_ra, S_dc) = (-T_dc, T_ra).
    """

    # Basic checks / normalization
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
    # Guard against tiny negative values from rounding (near poles)
    fac_pol = np.sqrt(np.clip(1.0 - x * x, 0.0, 1.0))

    # A_lm and B_lm recursion buffers
    A_mat = np.zeros((l_max + 1, l_max + 1, N), dtype=float)
    B_mat = np.zeros((l_max + 1, l_max + 1, N), dtype=float)
    B_mat[1, 1, :] = 1.0  # seed
    B_mat[1, 0, :] = 0.0

    # Output buffers (complex)
    T_ra_mat = np.zeros((l_max + 1, l_max + 1, N), dtype=complex)
    T_dc_mat = np.zeros((l_max + 1, l_max + 1, N), dtype=complex)

    # Build B_lm (Eqs. B.13–B.17)
    for l in range(2, l_max + 1):
        for m in range(l, -1, -1):  # m = l, l-1, ..., 0
            if m == 0:
                B_mat[l, 0, :] = 0.0
            elif l == m:
                # (2m-1) * m/(m-1) * sqrt(1-x^2) * B_{m-1,m-1}
                B_mat[l, m, :] = fac_pol * \
                    (2 * m - 1) * (m / (m - 1)) * B_mat[m - 1, m - 1, :]
            elif l == m + 1:
                # (2m+1) * x * B_{m,m}
                B_mat[l, m, :] = (2 * m + 1) * x * B_mat[m, m, :]
            else:
                # ((2l-1)x B_{l-1,m} - (l-1+m) B_{l-2,m}) / (l-m)
                B_mat[l, m, :] = ((2 * l - 1) * x * B_mat[l - 1, m, :] -
                                  (l - 1 + m) * B_mat[l - 2, m, :]) / (l - m)

    # Build A_lm (Eqs. B.18–B.19)
    for l in range(1, l_max + 1):
        for m in range(0, l + 1):
            if m == 0:
                A_mat[l, 0, :] = fac_pol * B_mat[l, 1, :]
            else:
                # (-x*l*B_{l,m} + (l+m)B_{l-1,m}) / m
                A_mat[l, m, :] = (-x * l * B_mat[l, m, :] +
                                  (l + m) * B_mat[l - 1, m, :]) / m

    # Project to e_ra, e_dec (Eqs. B.9–B.10)
    for l in range(1, l_max + 1):
        for m in range(0, l + 1):
            # Normalization coefficient
            c = (2 * l + 1) / (l * (l + 1)) / (4 * pi) * \
                factorial(l - m) / factorial(l + m)
            c = (-1) ** m * sqrt(c) * (cos(m * ra) + 1j * sin(m * ra))

            T_ra_mat[l, m, :] = c * A_mat[l, m, :]
            T_dc_mat[l, m, :] = c * B_mat[l, m, :] * (-1j)

    if sph_type == "T":
        return T_ra_mat, T_dc_mat
    elif sph_type == "S":
        # S = (-T_dc, T_ra)
        return -T_dc_mat, T_ra_mat
    else:
        raise ValueError("sph_type must be 'T' or 'S'.")


def real_vec_sph_harm_proj(
    l: int,
    m: int,
    T_ra_mat: np.ndarray,
    T_dc_mat: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Real-valued VSH components for given (l, m) from complex T_lm projections.

    Parameters
    ----------
    l, m : int
        Degree and order (with 0 <= m <= l).
    T_ra_mat, T_dc_mat : complex ndarray
        Outputs of `vec_sph_harm_proj(...)`.

    Returns
    -------
    T_ra_r, T_dc_r, T_ra_i, T_dc_i : float ndarray
        Real and imaginary parts (with the conventional sign: imag parts negated
        compared to the raw complex imag) as used in real expansions.
        If m == 0, returns (real(T_ra), real(T_dc), zeros, zeros).
    """
    if not (0 <= m <= l):
        raise ValueError("Require 0 <= m <= l.")

    T_ra = T_ra_mat[l, m, :]
    T_dc = T_dc_mat[l, m, :]

    if m == 0:
        # Only the "real" component is used for m = 0
        return np.real(T_ra), np.real(T_dc), np.zeros_like(T_ra, dtype=float), np.zeros_like(T_dc, dtype=float)

    # For m > 0, real basis uses:
    # real part unchanged, imag part with opposite sign and factor 2
    T_ra_r = 2.0 * np.real(T_ra)
    T_dc_r = 2.0 * np.real(T_dc)
    T_ra_i = -2.0 * np.imag(T_ra)
    T_dc_i = -2.0 * np.imag(T_dc)

    return T_ra_r, T_dc_r, T_ra_i, T_dc_i
