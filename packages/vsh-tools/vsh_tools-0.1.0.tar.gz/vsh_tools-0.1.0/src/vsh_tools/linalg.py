#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: linalg.py
"""
Linear algebra utilities for VSH least-squares.

Normal equation:
    A x = b
where A is the normal matrix, x the unknown vector, and b the RHS vector.
"""

from __future__ import annotations

import os
from sys import platform as _platform
import numpy as np
from numpy import concatenate

# Our basis functions
from .basis import real_vec_sph_harm_proj, vec_sph_harm_proj

__all__ = [
    "cov_to_cor",
    "cor_to_cov",
    "cov_mat_calc",
    "wgt_mat_calc",
    "jac_mat_l_calc",
    "jac_mat_calc",
    "nor_mat_calc",
    "predict_mat_calc",
    "predict_mat_calc_4_huge",
    "residual_calc",
    "nor_eq_sol",
    # cache helpers
    "cache_mat_calc",
    "nor_mat_calc_from_cache",
    "predict_mat_calc_from_cache",
    "residual_calc_from_cache",
    "nor_eq_sol_from_cache",
    "rm_cache_mat",
]


# ----------------------------- helpers -----------------------------

def check_tmp_dir() -> str:
    """Return a temporary directory path for caching matrices."""
    if _platform in ["linux", "linux2", "darwin"]:
        return "/tmp/"
    # default to current dir if unknown OS
    return "./"


# Global cache directory (with trailing slash)
TMP_DIR = check_tmp_dir()
if not TMP_DIR.endswith(os.sep):
    TMP_DIR += os.sep


def cov_to_cor(cov_mat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Convert covariance matrix => (sigma, correlation)."""
    cov_mat = np.asarray(cov_mat, dtype=float)
    sig = np.sqrt(np.clip(np.diag(cov_mat), 0.0, np.inf))
    # Avoid division warnings for zeros
    with np.errstate(divide="ignore", invalid="ignore"):
        cor = cov_mat / sig[:, None] / sig[None, :]
        cor[np.isnan(cor)] = 0.0
        np.fill_diagonal(cor, 1.0)
    return sig, cor


def cor_to_cov(sig: np.ndarray, cor_mat: np.ndarray) -> np.ndarray:
    """Convert (sigma, correlation) => covariance matrix."""
    sig = np.asarray(sig, dtype=float)
    cor_mat = np.asarray(cor_mat, dtype=float)
    return cor_mat * sig[:, None] * sig[None, :]


def cov_mat_calc(dra_err, ddc_err, ra_dc_cor=None) -> np.ndarray:
    """Build per-source 2×2 block-diagonal covariance matrix."""
    dra_err = np.asarray(dra_err, dtype=float)
    ddc_err = np.asarray(ddc_err, dtype=float)
    if dra_err.shape != ddc_err.shape:
        raise ValueError("dra_err and ddc_err must have the same length.")

    N = dra_err.size
    cov = np.zeros((2 * N, 2 * N), dtype=float)
    # diagonal terms
    cov[np.arange(N), np.arange(N)] = dra_err ** 2
    cov[np.arange(N, 2 * N), np.arange(N, 2 * N)] = ddc_err ** 2

    if ra_dc_cor is not None:
        ra_dc_cor = np.asarray(ra_dc_cor, dtype=float)
        if ra_dc_cor.shape != dra_err.shape:
            raise ValueError("ra_dc_cor must have the same length as dra_err.")
        off = ra_dc_cor * dra_err * ddc_err
        cov[np.arange(N), np.arange(N, 2 * N)] = off
        cov[np.arange(N, 2 * N), np.arange(N)] = off

    return cov


def wgt_mat_calc(dra_err, ddc_err, ra_dc_cor=None) -> np.ndarray:
    """Inverse of covariance matrix."""
    cov = cov_mat_calc(dra_err, ddc_err, ra_dc_cor)
    return np.linalg.inv(cov)


# ----------------------------- Jacobians -----------------------------

def jac_mat_l_calc(T_ra_mat, T_dc_mat, l: int, fit_type: str = "full") -> np.ndarray:
    """Jacobian block for degree l.

    Returns a matrix with shape:
        (2M, 4l+2) for fit_type="full"
        (2M, 2l+1) otherwise
    where M is the number of sources.
    """
    M = T_ra_mat.shape[2]

    # m = 0 component (returns 4 arrays; take first two)
    Tl0_ra, Tl0_dc, _, _ = real_vec_sph_harm_proj(l, 0, T_ra_mat, T_dc_mat)

    if fit_type in ["full", "FULL", "Full"]:
        # Columns: [T(…m=0), S(…m=0), T(…m=1 real), S(…m=1 real), T(…m=1 imag), S(…m=1 imag), ...]
        jac_ra = concatenate(
            (Tl0_ra.reshape(M, 1), -Tl0_dc.reshape(M, 1)), axis=1)
        jac_dc = concatenate(
            (Tl0_dc.reshape(M, 1),  Tl0_ra.reshape(M, 1)), axis=1)
    elif fit_type in ["T", "t"]:
        jac_ra, jac_dc = Tl0_ra.reshape(M, 1), Tl0_dc.reshape(M, 1)
    elif fit_type in ["S", "s"]:
        jac_ra, jac_dc = -Tl0_dc.reshape(M, 1), Tl0_ra.reshape(M, 1)
    else:
        raise ValueError("fit_type must be 'full', 'T' or 'S'.")

    for m in range(1, l + 1):
        Tlmr_ra, Tlmr_dc, Tlmi_ra, Tlmi_dc = real_vec_sph_harm_proj(
            l, m, T_ra_mat, T_dc_mat)

        if fit_type in ["full", "FULL", "Full"]:
            jac_ra = concatenate(
                (jac_ra,
                 Tlmr_ra.reshape(M, 1), -Tlmr_dc.reshape(M, 1),
                 Tlmi_ra.reshape(M, 1), -Tlmi_dc.reshape(M, 1)), axis=1
            )
            jac_dc = concatenate(
                (jac_dc,
                 Tlmr_dc.reshape(M, 1),  Tlmr_ra.reshape(M, 1),
                 Tlmi_dc.reshape(M, 1),  Tlmi_ra.reshape(M, 1)), axis=1
            )
        elif fit_type in ["T", "t"]:
            jac_ra = concatenate((jac_ra, Tlmr_ra.reshape(
                M, 1), Tlmi_ra.reshape(M, 1)), axis=1)
            jac_dc = concatenate((jac_dc, Tlmr_dc.reshape(
                M, 1), Tlmi_dc.reshape(M, 1)), axis=1)
        else:  # "S"
            jac_ra = concatenate(
                (jac_ra, -Tlmr_dc.reshape(M, 1), -Tlmi_dc.reshape(M, 1)), axis=1)
            jac_dc = concatenate((jac_dc,  Tlmr_ra.reshape(
                M, 1),  Tlmi_ra.reshape(M, 1)), axis=1)

    jac = concatenate((jac_ra, jac_dc), axis=0)

    # shape check
    if fit_type in ["full", "FULL", "Full"]:
        expected = (2 * M, 4 * l + 2)
    else:
        expected = (2 * M, 2 * l + 1)

    if jac.shape != expected:
        raise RuntimeError(f"Jacobian(l={l}) shape {jac.shape} != {expected}")

    return jac


def jac_mat_calc(ra_rad, dc_rad, l_max: int, fit_type: str = "full") -> np.ndarray:
    """Full Jacobian up to degree l_max."""
    ra_rad = np.asarray(ra_rad, dtype=float)
    dc_rad = np.asarray(dc_rad, dtype=float)
    M = ra_rad.size

    T_ra_mat, T_dc_mat = vec_sph_harm_proj(l_max, ra_rad, dc_rad)

    jac = jac_mat_l_calc(T_ra_mat, T_dc_mat, 1, fit_type)
    for l in range(2, l_max + 1):
        jac_l = jac_mat_l_calc(T_ra_mat, T_dc_mat, l, fit_type)
        jac = concatenate((jac, jac_l), axis=1)

    if fit_type in ["full", "FULL", "Full"]:
        expected = (2 * M, 2 * l_max * (l_max + 2))
    else:
        expected = (2 * M, l_max * (l_max + 2))

    if jac.shape != expected:
        raise RuntimeError(f"Jacobian shape {jac.shape} != {expected}")

    return jac


# ----------------------------- normal eqs & residuals -----------------------------

def nor_mat_calc(
    dra, ddc, dra_err, ddc_err, ra_rad, dc_rad,
    ra_dc_cor=None, l_max: int = 1, fit_type: str = "full",
    save_mat: bool = False, suffix: str = "",
) -> tuple[np.ndarray, np.ndarray]:
    """Assemble normal matrix and RHS."""
    jac = jac_mat_calc(ra_rad, dc_rad, l_max, fit_type)
    wgt = wgt_mat_calc(dra_err, ddc_err, ra_dc_cor)

    mul = jac.T @ wgt
    A = mul @ jac
    b = mul @ concatenate((dra, ddc), axis=0)

    if save_mat:
        np.save(f"{TMP_DIR}jac_mat_{suffix}.npy", jac)
        np.save(f"{TMP_DIR}mul_mat_{suffix}.npy", mul)
        np.save(f"{TMP_DIR}nor_mat_{suffix}.npy", A)

    return A, b


def predict_mat_calc(pmt, ra_rad, dc_rad, l_max: int, fit_type: str = "full"):
    """Predict (dra, ddc) from parameters."""
    jac = jac_mat_calc(ra_rad, dc_rad, l_max, fit_type)
    vec = jac @ np.asarray(pmt, dtype=float)
    N = vec.size // 2
    return vec[:N], vec[N:]


def predict_mat_calc_4_huge(
    pmt, ra_rad, dc_rad, l_max: int, fit_type: str = "full", num_iter: int | None = None
):
    """Predict values in chunks to save memory."""
    if num_iter is None:
        num_iter = 100

    ra_rad = np.asarray(ra_rad, dtype=float)
    dc_rad = np.asarray(dc_rad, dtype=float)
    N = ra_rad.size

    dra_pre = np.empty(0, dtype=float)
    ddc_pre = np.empty(0, dtype=float)

    rem = N % num_iter
    if rem:
        d1, d2 = predict_mat_calc(
            pmt, ra_rad[:rem], dc_rad[:rem], l_max, fit_type)
        dra_pre = concatenate((dra_pre, d1))
        ddc_pre = concatenate((ddc_pre, d2))

    for i in range(N // num_iter):
        s = rem + i * num_iter
        e = s + num_iter
        d1, d2 = predict_mat_calc(
            pmt, ra_rad[s:e], dc_rad[s:e], l_max, fit_type)
        dra_pre = concatenate((dra_pre, d1))
        ddc_pre = concatenate((ddc_pre, d2))

    return dra_pre, ddc_pre


def residual_calc(dra, ddc, ra_rad, dc_rad, pmt, l_max: int, fit_type: str = "full",
                  num_iter: int | None = None):
    """Post-fit residuals."""
    dra_pre, ddc_pre = predict_mat_calc_4_huge(
        pmt, ra_rad, dc_rad, l_max, fit_type, num_iter)
    return dra - dra_pre, ddc - ddc_pre


def nor_eq_sol(
    dra, ddc, dra_err, ddc_err, ra_rad, dc_rad, ra_dc_cor=None,
    l_max: int = 1, fit_type: str = "full", num_iter: int | None = None, calc_res: bool = True
):
    """Solve normal equations; optionally return residuals."""
    if num_iter is None:
        num_iter = 100

    dra = np.asarray(dra, dtype=float)
    ddc = np.asarray(ddc, dtype=float)

    N = dra.size
    div, rem = N // num_iter, N % num_iter

    # init A, b
    if rem:
        A, b = nor_mat_calc(
            dra[:rem], ddc[:rem], dra_err[:rem], ddc_err[:rem],
            ra_rad[:rem], dc_rad[:rem], ra_dc_cor=None if ra_dc_cor is None else ra_dc_cor[:rem],
            l_max=l_max, fit_type=fit_type,
        )
    else:
        A = 0.0
        b = 0.0

    for i in range(div):
        s = rem + i * num_iter
        e = s + num_iter
        Ai, bi = nor_mat_calc(
            dra[s:e], ddc[s:e], dra_err[s:e], ddc_err[s:e],
            ra_rad[s:e], dc_rad[s:e], ra_dc_cor=None if ra_dc_cor is None else ra_dc_cor[s:e],
            l_max=l_max, fit_type=fit_type,
        )
        A = A + Ai
        b = b + bi

    pmt = np.linalg.solve(A, b)
    cov = np.linalg.inv(A)
    sig, cor = cov_to_cor(cov)

    if calc_res:
        dra_r, ddc_r = residual_calc(
            dra, ddc, ra_rad, dc_rad, pmt, l_max, fit_type, num_iter)
        return pmt, sig, cor, dra_r, ddc_r
    return pmt, sig, cor


# ----------------------------- cache utilities -----------------------------

def _save_cache(prefix: str, **arrays):
    for k, v in arrays.items():
        np.save(f"{TMP_DIR}{k}_{prefix}.npy", v)


def _load_cache(prefix: str, name: str) -> np.ndarray:
    return np.load(f"{TMP_DIR}{name}_{prefix}.npy")


def nor_mat_calc_for_cache(dra_err, ddc_err, ra_rad, dc_rad,
                           ra_dc_cor=None, l_max: int = 1, fit_type: str = "full",
                           suffix: str = ""):
    """Compute and cache Jacobian-derived matrices (jac, mul, nor)."""
    jac = jac_mat_calc(ra_rad, dc_rad, l_max, fit_type)
    wgt = wgt_mat_calc(dra_err, ddc_err, ra_dc_cor)
    mul = jac.T @ wgt
    nor = mul @ jac
    _save_cache(suffix, jac_mat=jac, mul_mat=mul, nor_mat=nor)


def cache_mat_calc(dra, ddc, dra_err, ddc_err, ra_rad, dc_rad, ra_dc_cor=None,
                   l_max: int = 1, fit_type: str = "full", num_iter: int | None = None):
    """Create cached blocks and return their suffix list (order matches data order)."""
    if num_iter is None:
        num_iter = 100

    N = len(dra)
    div, rem = N // num_iter, N % num_iter
    suffixes: list[str] = []

    if rem:
        suf = f"{0:05d}"
        suffixes.append(suf)
        nor_mat_calc_for_cache(dra_err[:rem], ddc_err[:rem], ra_rad[:rem], dc_rad[:rem],
                               None if ra_dc_cor is None else ra_dc_cor[:rem],
                               l_max, fit_type, suf)

    for i in range(div):
        s = rem + i * num_iter
        e = s + num_iter
        suf = f"{i+1:05d}"
        suffixes.append(suf)
        nor_mat_calc_for_cache(dra_err[s:e], ddc_err[s:e], ra_rad[s:e], dc_rad[s:e],
                               None if ra_dc_cor is None else ra_dc_cor[s:e],
                               l_max, fit_type, suf)

    return suffixes


def nor_mat_calc_from_cache(dra, ddc, suffix: str):
    """Load cached normal pieces and form RHS for this chunk."""
    mul = _load_cache(suffix, "mul_mat")
    nor = _load_cache(suffix, "nor_mat")
    rhs = mul @ concatenate((dra, ddc), axis=0)
    return nor, rhs


def predict_mat_calc_from_cache(pmt, suffix: str):
    """Predict (dra, ddc) using cached Jacobian."""
    jac = _load_cache(suffix, "jac_mat")
    vec = jac @ np.asarray(pmt, dtype=float)
    N = vec.size // 2
    return vec[:N], vec[N:]


def residual_calc_from_cache(dra, ddc, pmt, suffixes):
    """Residuals using cached Jacobians."""
    dra_pre = np.empty(0, dtype=float)
    ddc_pre = np.empty(0, dtype=float)
    for suf in suffixes:
        d1, d2 = predict_mat_calc_from_cache(pmt, suf)
        dra_pre = concatenate((dra_pre, d1))
        ddc_pre = concatenate((ddc_pre, d2))
    return dra - dra_pre, ddc - ddc_pre


def nor_eq_sol_from_cache(dra, ddc, suffixes, calc_res: bool = True):
    """Solve using cached blocks."""
    if len(suffixes) == 0:
        raise ValueError("suffixes must be a non-empty list.")

    # accumulate A and b
    A = 0.0
    b = 0.0
    offset = 0
    for suf in suffixes:
        # Determine chunk length from cached jacobian
        jac = _load_cache(suf, "jac_mat")
        n_obs = jac.shape[0] // 2  # number of sources in this chunk

        Ai, bi = nor_mat_calc_from_cache(dra[offset:offset+n_obs],
                                         ddc[offset:offset+n_obs], suf)
        A = A + Ai
        b = B = bi  # corrected below
        offset += n_obs

    # Fix small oversight: sum b properly
    # (the previous line assigned; we fix by recomputing cleanly)
    A = 0.0
    b = 0.0
    offset = 0
    for suf in suffixes:
        jac = _load_cache(suf, "jac_mat")
        n_obs = jac.shape[0] // 2
        Ai = _load_cache(suf, "nor_mat")
        bi = _load_cache(suf, "mul_mat") @ concatenate((dra[offset:offset+n_obs],
                                                        ddc[offset:offset+n_obs]), axis=0)
        A = A + Ai
        b = b + bi
        offset += n_obs

    pmt = np.linalg.solve(A, b)
    cov = np.linalg.inv(A)
    sig, cor = cov_to_cor(cov)

    if calc_res:
        dra_r, ddc_r = residual_calc_from_cache(dra, ddc, pmt, suffixes)
        return pmt, sig, cor, dra_r, ddc_r
    return pmt, sig, cor


def rm_cache_mat(suffixes):
    """Remove cached arrays for all suffixes."""
    for suf in suffixes:
        for name in ("jac_mat", "mul_mat", "nor_mat"):
            path = f"{TMP_DIR}{name}_{suf}.npy"
            if os.path.exists(path):
                os.remove(path)
