#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: stats.py
"""
Basic statistics for VSH workflows:
- weighted mean
- (weighted) WRMS / std of residuals
- chi-square (1D / 2D)
- goodness-of-fit (p-value)
- robust scatter estimate (RSE)
"""

import numpy as np
from scipy.special import gammaincc

__all__ = [
    "calc_mean",
    "calc_wrms",
    "calc_chi2",
    "calc_nor_sep",
    "calc_chi2_2d",
    "calc_chi2_from_nor_sep",
    "calc_gof",
    "calc_rse",
]


# -----------------------------  FUNCTIONS -----------------------------
def calc_mean(x, err=None):
    """Weighted mean (weights = 1/err^2) or plain mean if err is None."""
    x = np.asarray(x, dtype=float)

    if err is None:
        return float(np.mean(x))

    err = np.asarray(err, dtype=float)
    if x.shape != err.shape:
        raise ValueError("x and err must have the same shape.")

    w = 1.0 / (err ** 2)
    # Guard against zero/inf weights
    valid = np.isfinite(w) & (w > 0)
    if not np.any(valid):
        raise ValueError("All weights are non-positive or invalid.")
    w = w[valid]
    xv = x[valid]
    return float(np.dot(xv, w) / np.sum(w))


def calc_wrms(x, err=None, bias=None):
    """
    Weighted root-mean-square of (x - bias).

    If err is None:
        wrms = sqrt( sum((x - mean)^2) / (N - 1) ) if bias is None,
               sqrt( sum((x - bias)^2) / (N - 1) ) otherwise.
    If err is provided (weights = 1/err^2):
        wrms = sqrt( sum(((x - bias)^2) / err^2) / sum(1/err^2) ),
        where bias defaults to the weighted mean.
    """
    x = np.asarray(x, dtype=float)

    if err is None:
        if bias is None:
            bias = float(np.mean(x))
        xn = x - bias
        denom = max(len(x) - 1, 1)
        return float(np.sqrt(np.dot(xn, xn) / denom))

    err = np.asarray(err, dtype=float)
    if x.shape != err.shape:
        raise ValueError("x and err must have the same shape.")

    w = 1.0 / (err ** 2)
    valid = np.isfinite(w) & (w > 0)
    if not np.any(valid):
        raise ValueError("All weights are non-positive or invalid.")
    x = x[valid]
    w = w[valid]

    if bias is None:
        # weighted mean with weights w
        bias = float(np.dot(x, w) / np.sum(w))

    xn = x - bias
    return float(np.sqrt(np.dot(xn * xn, w) / np.sum(w)))


def calc_chi2(x, err, reduced=False, num_dof=None):
    """Chi-square; if reduced=True, divide by num_dof (must be provided)."""
    x = np.asarray(x, dtype=float)
    err = np.asarray(err, dtype=float)
    if x.shape != err.shape:
        raise ValueError("x and err must have the same shape.")

    with np.errstate(divide="ignore", invalid="ignore"):
        r = x / err
        r[~np.isfinite(r)] = 0.0
    chi2 = float(np.dot(r, r))

    if reduced:
        if num_dof is None:
            raise ValueError("num_dof must be provided when reduced=True.")
        chi2 /= float(num_dof)

    return chi2


def calc_nor_sep(x, x_err, y, y_err, xy_cor=None):
    """
    Normalized separation considering correlation:
    n^2 = (nx^2 + ny^2 - 2ρ nx ny) / (1 - ρ^2), with nx=x/x_err, ny=y/y_err.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x_err = np.asarray(x_err, dtype=float)
    y_err = np.asarray(y_err, dtype=float)

    if not (x.shape == y.shape == x_err.shape == y_err.shape):
        raise ValueError("All inputs must have the same shape.")

    with np.errstate(divide="ignore", invalid="ignore"):
        nx = x / x_err
        ny = y / y_err
        nx[~np.isfinite(nx)] = 0.0
        ny[~np.isfinite(ny)] = 0.0

    n2 = nx**2 + ny**2

    if xy_cor is not None:
        rho = np.asarray(xy_cor, dtype=float)
        if rho.shape != x.shape:
            raise ValueError("xy_cor must have the same shape as x.")
        denom = 1.0 - rho**2
        # Avoid division by ~0 when |rho|≈1
        denom = np.where(denom <= 1e-15, 1e-15, denom)
        n2 = (n2 - 2.0 * rho * nx * ny) / denom

    n2 = np.maximum(n2, 0.0)
    return np.sqrt(n2)


def calc_chi2_2d(x, x_err, y, y_err, xy_cor=None, num_dof=None):
    """2D chi-square from normalized separations; divide by num_dof if provided."""
    nor_sep = calc_nor_sep(x, x_err, y, y_err, xy_cor)
    chi2 = float(np.sum(nor_sep**2))
    if num_dof is not None:
        chi2 /= float(num_dof)
    return chi2


def calc_chi2_from_nor_sep(nor_sep, num_dof=None):
    """Chi-square directly from normalized separations."""
    nor_sep = np.asarray(nor_sep, dtype=float)
    chi2 = float(np.sum(nor_sep**2))
    if num_dof is not None:
        chi2 /= float(num_dof)
    return chi2


def calc_gof(num_dof, chi2):
    """
    Goodness-of-fit Q = gammaincc(k/2, chi2/2), where k=num_dof.
    Equivalent to the (upper) survival function for the chi-square distribution.
    """
    return float(gammaincc(0.5 * float(num_dof), 0.5 * float(chi2)))


def calc_rse(x):
    """Robust Scatter Estimate (RSE) used by Gaia: 0.390152 * (P90 - P10)."""
    x = np.asarray(x, dtype=float)
    x10, x90 = np.percentile(x, [10, 90])
    return float(0.390152 * (x90 - x10))
