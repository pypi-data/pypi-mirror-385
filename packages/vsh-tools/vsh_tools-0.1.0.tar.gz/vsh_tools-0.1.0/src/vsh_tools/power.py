#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: power.py
"""
Power diagnostics for Vector Spherical Harmonics (VSH).

- Degree-wise power for a single component (T or S)
- Split-and-evaluate power for full (T+S) fits
- Total field power (Eq. 74 in Mignard & Klioner 2012)
- Remaining power curve after subtracting degrees progressively
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "calc_vsh_power_lm",
    "calc_vsh_power_l",
    "calc_vsh_power",
    "calc_field_power",
    "calc_rem_power",
]


# -----------------------------  CORE -----------------------------
def calc_vsh_power_lm(ts_lm, l: int) -> float:
    """
    Degree-l power for a single component (T or S).

    Parameters
    ----------
    ts_lm : array_like, shape (2*l+1,)
        Coefficients for m = 0, ±1, …, ±l, arranged as
        [m=0, Re(m=1), Im(m=1), ..., Re(m=l), Im(m=l)]
        i.e., the usual "real basis" packing that results in (2l+1) numbers.
    l : int
        Harmonic degree (>= 1).

    Returns
    -------
    P_l : float
        Degree-l power for this component.
    """
    ts_lm = np.asarray(ts_lm, dtype=float)
    if ts_lm.size != 2 * l + 1:
        raise ValueError(f"ts_lm length {ts_lm.size} != 2*l+1 = {2*l+1}")

    ts2 = ts_lm * ts_lm
    # 2 * sum_{m>=0} (Re^2 + Im^2) - (m=0 term counted once)
    return float(2.0 * np.sum(ts2) - ts2[0])


def calc_vsh_power(ts_pmt, l_max: int, fit_type: str = "full") -> tuple[np.ndarray, np.ndarray]:
    """
    Power spectra (per degree) for toroidal (T) and spheroidal (S) components.

    Parameters
    ----------
    ts_pmt : array_like
        Packed real-basis coefficients across degrees 1..l_max.
        Length depends on fit_type:
          - "full": 2 * l_max * (l_max + 2)   (interleaved T,S,T,S,... per coefficient)
          - "T" or "S":     l_max * (l_max + 2)
    l_max : int
        Maximum degree (>= 1).
    fit_type : {"full","T","S"} (case-insensitive)

    Returns
    -------
    P_t, P_s : ndarray, shape (l_max,)
        Degree-wise power for T and S. If only one type was fitted, the other is zeros.
    """
    l_max = int(l_max)
    if l_max < 1:
        raise ValueError("l_max must be >= 1.")

    ts_pmt = np.asarray(ts_pmt, dtype=float)
    n_single = l_max * (l_max + 2)  # sum_{l=1..L} (2l+1)

    f = fit_type.lower()
    if f == "full":
        expected = 2 * n_single
        if ts_pmt.size != expected:
            raise ValueError(
                f"ts_pmt length {ts_pmt.size} != {expected} for full fit.")
        # Interleaved storage: [T0,S0, T1,S1, ...]
        t_pmt = ts_pmt[0::2]
        s_pmt = ts_pmt[1::2]
    elif f == "t":
        expected = n_single
        if ts_pmt.size != expected:
            raise ValueError(
                f"ts_pmt length {ts_pmt.size} != {expected} for T-only fit.")
        t_pmt = ts_pmt
        s_pmt = np.zeros_like(t_pmt)
    elif f == "s":
        expected = n_single
        if ts_pmt.size != expected:
            raise ValueError(
                f"ts_pmt length {ts_pmt.size} != {expected} for S-only fit.")
        s_pmt = ts_pmt
        t_pmt = np.zeros_like(s_pmt)
    else:
        raise ValueError(
            "fit_type must be one of {'full','T','S'} (case-insensitive).")

    P_t = calc_vsh_power_l(t_pmt, l_max)
    P_s = calc_vsh_power_l(s_pmt, l_max)
    return P_t, P_s


def calc_vsh_power_l(ts_pmt, l_max: int) -> np.ndarray:
    """
    Degree-wise power for a single component (T or S).

    Parameters
    ----------
    ts_pmt : array_like, length l_max*(l_max+2)
        Packed real-basis coefficients across degrees 1..l_max.
        Layout per degree l: (2l+1) values as in `calc_vsh_power_lm`.
    l_max : int
        Maximum degree.

    Returns
    -------
    P_l : ndarray, shape (l_max,)
        Power per degree.
    """
    ts_pmt = np.asarray(ts_pmt, dtype=float)
    expected = l_max * (l_max + 2)
    if ts_pmt.size != expected:
        raise ValueError(
            f"ts_pmt length {ts_pmt.size} != l_max*(l_max+2) = {expected}")

    P = np.zeros(l_max, dtype=float)
    end = 0
    for l in range(1, l_max + 1):
        sta, end = end, end + (2 * l + 1)
        P[l - 1] = calc_vsh_power_lm(ts_pmt[sta:end], l)
    return P


# -----------------------------  FIELD -----------------------------
def calc_field_power(dra, ddc) -> float:
    """
    Total power of the 2D vector field (Eq. 74).

    Parameters
    ----------
    dra, ddc : array_like
        Tangential components (e.g., Δα⋅cosδ and Δδ) in consistent units.

    Returns
    -------
    P_field : float
        4π/N * Σ (dra^2 + ddc^2)
    """
    dra = np.asarray(dra, dtype=float)
    ddc = np.asarray(ddc, dtype=float)
    if dra.shape != ddc.shape:
        raise ValueError("dra and ddc must have the same shape.")
    N = dra.size
    if N == 0:
        return 0.0
    return float(4.0 * np.pi / N * np.sum(dra * dra + ddc * ddc))


def calc_rem_power(P_tot, P_field: float, l_max: int) -> np.ndarray:
    """
    Remaining power after subtracting degrees cumulatively.

    Parameters
    ----------
    P_tot : array_like, shape (l_max,)
        Total power per degree (e.g., P_t + P_s).
    P_field : float
        Total field power.
    l_max : int
        Maximum degree.

    Returns
    -------
    P_rem : ndarray, shape (l_max+1,)
        Remaining power after subtracting up to degree k (k=0..l_max).
        P_rem[0] = P_field; P_rem[k] = P_field - sum_{i=1..k} P_tot[i-1]
    """
    P_tot = np.asarray(P_tot, dtype=float)
    if P_tot.size != l_max:
        raise ValueError("P_tot must have length l_max.")
    P_rem = np.empty(l_max + 1, dtype=float)
    P_rem[0] = float(P_field)
    if l_max:
        P_rem[1:] = P_field - np.cumsum(P_tot)
    return P_rem
