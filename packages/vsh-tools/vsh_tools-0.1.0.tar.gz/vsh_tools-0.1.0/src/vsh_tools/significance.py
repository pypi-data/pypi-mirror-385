#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: significance.py
"""
Significance diagnostics for VSH:
- normalized power statistics (three flavors)
- Z-statistics per degree
- overall printout combining field power and remaining power
"""

from __future__ import annotations

import numpy as np
from numpy import sqrt

# Our power helpers
from .power import (
    calc_vsh_power_lm,
    calc_vsh_power,
    calc_rem_power,
    calc_field_power,
)

__all__ = [
    "calc_vsh_nor_power_lm1",
    "calc_vsh_nor_power_lm2",
    "calc_vsh_nor_power_lm3",
    "calc_vsh_nor_power_l",
    "calc_vsh_nor_power",
    "calc_Z_lm",
    "calc_Z",
    "check_vsh_sig",
]


# ----------------------------- normalized power per degree -----------------------------

def _check_len_match(ts_lm, ts_lm_err, l):
    ts_lm = np.asarray(ts_lm, dtype=float)
    ts_lm_err = np.asarray(ts_lm_err, dtype=float)
    if ts_lm.size != (2 * l + 1):
        raise ValueError(f"ts_lm length {ts_lm.size} != 2*l+1 = {2*l+1}")
    if ts_lm_err.size != ts_lm.size:
        raise ValueError("ts_lm and ts_lm_err must have the same length.")
    return ts_lm, ts_lm_err


def calc_vsh_nor_power_lm1(ts_lm, ts_lm_err, l: int) -> float:
    """
    Normalized power #1 (Eq. 83):  W₁ = P_l / σ_{l0}²
    """
    ts_lm, ts_lm_err = _check_len_match(ts_lm, ts_lm_err, l)
    P_l = calc_vsh_power_lm(ts_lm, l)
    sigma2_l0 = float(ts_lm_err[0] ** 2)
    if sigma2_l0 <= 0:
        raise ValueError("Variance of the m=0 term must be positive.")
    return float(P_l / sigma2_l0)


def calc_vsh_nor_power_lm2(ts_lm, ts_lm_err, l: int) -> float:
    """
    Normalized power #2 (Eq. 86):  W₂ = Σ_m ( c_{lm} / σ_{lm} )²
    """
    ts_lm, ts_lm_err = _check_len_match(ts_lm, ts_lm_err, l)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = ts_lm / ts_lm_err
        r[~np.isfinite(r)] = 0.0
    return float(np.sum(r * r))


def calc_vsh_nor_power_lm3(ts_lm, ts_lm_err, l: int) -> float:
    """
    Normalized power #3 (Eq. 87):  W₃ = P_l / ⟨σ²⟩  with m=0 counted once.
    """
    ts_lm, ts_lm_err = _check_len_match(ts_lm, ts_lm_err, l)
    P_l = calc_vsh_power_lm(ts_lm, l)
    v = ts_lm_err ** 2
    mean_sigma2 = float((2.0 * np.sum(v) - v[0]) / (2 * l + 1))
    if mean_sigma2 <= 0:
        raise ValueError("Average variance must be positive.")
    return float(P_l / mean_sigma2)


def calc_vsh_nor_power_l(ts_pmt, ts_pmt_err, l_max: int, nor_type: str = "3") -> np.ndarray:
    """
    Degree-wise normalized power for a single component (T or S).
    """
    if nor_type not in {"1", "2", "3"}:
        raise ValueError("nor_type must be one of {'1','2','3'}.")

    ts_pmt = np.asarray(ts_pmt, dtype=float)
    ts_pmt_err = np.asarray(ts_pmt_err, dtype=float)
    expected = l_max * (l_max + 2)
    if ts_pmt.size != expected:
        raise ValueError(
            f"ts_pmt length {ts_pmt.size} != l_max*(l_max+2) = {expected}")
    if ts_pmt_err.size != ts_pmt.size:
        raise ValueError("ts_pmt and ts_pmt_err must have the same length.")

    W = np.zeros(l_max, dtype=float)
    end = 0
    for l in range(1, l_max + 1):
        sta, end = end, end + (2 * l + 1)
        a = ts_pmt[sta:end]
        s = ts_pmt_err[sta:end]
        if nor_type == "1":
            W[l - 1] = calc_vsh_nor_power_lm1(a, s, l)
        elif nor_type == "2":
            W[l - 1] = calc_vsh_nor_power_lm2(a, s, l)
        else:
            W[l - 1] = calc_vsh_nor_power_lm3(a, s, l)
    return W


def calc_vsh_nor_power(
    ts_pmt, ts_pmt_err, l_max: int, nor_type: str = "3", fit_type: str = "f"
) -> tuple[np.ndarray, np.ndarray]:
    """
    Normalized power spectra (T and S) for degrees 1..l_max.

    Parameters
    ----------
    ts_pmt, ts_pmt_err : packed real-basis coefficients and their sigmas.
        If fit_type == "full": length = 2 * l_max * (l_max + 2), interleaved [T,S,T,S,...]
        If fit_type == "T" or "S": length = l_max * (l_max + 2)
    """
    ts_pmt = np.asarray(ts_pmt, dtype=float)
    ts_pmt_err = np.asarray(ts_pmt_err, dtype=float)

    single_len = l_max * (l_max + 2)
    f = fit_type.lower()
    if f == "full":
        expected = 2 * single_len
        if ts_pmt.size != expected or ts_pmt_err.size != expected:
            raise ValueError(f"Expect length {expected} for full fit.")
        t_pmt, t_sig = ts_pmt[0::2], ts_pmt_err[0::2]
        s_pmt, s_sig = ts_pmt[1::2], ts_pmt_err[1::2]
        W_t = calc_vsh_nor_power_l(t_pmt, t_sig, l_max, nor_type)
        W_s = calc_vsh_nor_power_l(s_pmt, s_sig, l_max, nor_type)
    elif f == "t":
        if ts_pmt.size != single_len or ts_pmt_err.size != single_len:
            raise ValueError(f"Expect length {single_len} for T-only fit.")
        W_t = calc_vsh_nor_power_l(ts_pmt, ts_pmt_err, l_max, nor_type)
        W_s = np.zeros_like(W_t)
    elif f == "s":
        if ts_pmt.size != single_len or ts_pmt_err.size != single_len:
            raise ValueError(f"Expect length {single_len} for S-only fit.")
        W_s = calc_vsh_nor_power_l(ts_pmt, ts_pmt_err, l_max, nor_type)
        W_t = np.zeros_like(W_s)
    else:
        raise ValueError(
            "fit_type must be one of {'full','T','S'} (case-insensitive).")

    return W_t, W_s


# ----------------------------- Z statistics -----------------------------

def calc_Z_lm(Wts_l: float, num_dof: int) -> float:
    """
    Z-statistics (Eq. 85) for a single degree l using Wilson–Hilferty transform.
    """
    k = float(num_dof)
    if k <= 0:
        raise ValueError("num_dof must be positive.")
    return float(sqrt(4.5 * k) * ((Wts_l / k) ** (1.0 / 3.0) - (1.0 - 2.0 / (9.0 * k))))


def calc_Z(Wts: np.ndarray) -> np.ndarray:
    """
    Z-statistics per degree; for degree l, num_dof = 2l + 1 (real basis).
    """
    Wts = np.asarray(Wts, dtype=float)
    Z = np.zeros_like(Wts)
    for l, W_l in enumerate(Wts, start=1):
        Z[l - 1] = calc_Z_lm(W_l, 2 * l + 1)
    return Z


# ----------------------------- top-level report -----------------------------

def check_vsh_sig(dra, ddc, ts_pmt, ts_pmt_err, l_max: int, fit_type: str = "f", nor_type: str = "3"):
    """
    Print a compact significance table:
    - sqrt power per degree for T and S
    - Z-statistics per degree
    - remaining power curve sqrt(P_rem)

    Parameters
    ----------
    dra, ddc : array_like
        Tangential field components (same length).
    ts_pmt, ts_pmt_err : array_like
        Packed real-basis coefficients and their sigmas.
    l_max : int
        Maximum degree.
    fit_type : {"full","T","S"}
    nor_type : {"1","2","3"}
    """
    dra = np.asarray(dra, dtype=float)
    ddc = np.asarray(ddc, dtype=float)
    if dra.shape != ddc.shape:
        raise ValueError("dra and ddc must have the same shape.")

    # Field power (Eq. 74)
    P_field = calc_field_power(dra, ddc)

    # Power per degree for T and S
    P_t, P_s = calc_vsh_power(ts_pmt, l_max, fit_type)

    # Remaining power (start with total field power)
    P_rem = calc_rem_power(P_t + P_s, P_field, l_max)

    # Normalized power W (choose flavor via nor_type)
    W_t, W_s = calc_vsh_nor_power(
        ts_pmt, ts_pmt_err, l_max, nor_type=nor_type, fit_type=fit_type)

    # Z per degree
    Z_t, Z_s = calc_Z(W_t), calc_Z(W_s)

    # Print
    print("Significance level")
    print("--------------------------------------------------------------------")
    print("Degree  P_t^0.5      Z_t   P_s^0.5      Z_s   P_rem^0.5")
    print("--------------------------------------------------------------------")
    # Total (degree 0 row)
    print(
        f"{0:6d}                                          {sqrt(P_rem[0]):6.1f}")
    for l in range(1, l_max + 1):
        i = l - 1
        print(
            f"{l:6d} {sqrt(P_t[i]):8.1f}   {Z_t[i]:6.2f}  {sqrt(P_s[i]):8.1f}   {Z_s[i]:6.2f}  {sqrt(P_rem[l]):9.1f}")
    print("--------------------------------------------------------------------")
