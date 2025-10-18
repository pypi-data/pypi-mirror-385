#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: legacy.py
"""
Created on Sat 18 Oct 2025 03:10:10 PM CST

@author: Neo(niu.liu@nju.edu.cn)


Legacy VSH analysis — consolidated, consistent, and self-contained.

This merges/modernizes classic utilities:
- Stats: weighted mean, WRMS, χ² (1D/2D), GOF.
- 2×2 per-source weighting (with correlation or covariance).
- Degree-1 and Degree-2 VSH Jacobians (rotation+glide [+ quadrupole]).
- Forward model (vsh_func) with consistent parameter ordering.
- Normal-equations solver with uncertainties/correlation.
- Outlier handling: sigma clip and Rayleigh-median clip.
- High-level fit API for degree 1 and degree 2.

Parameter ordering (coherent across Jacobians & models):

  deg-1 full: (g1, g2, g3, r1, r2, r3)
  deg-2 full: (g1, g2, g3, r1, r2, r3,
               ER_22, EI_22, ER_21, EI_21, E_20,
               MR_22, MI_22, MR_21, MI_21, M_20)

Units:
- ra/dec inputs to fit_* must be in degrees (converted internally to rad).
- dra/ddec and their errors are any consistent linear unit (e.g., μas).
"""

from __future__ import annotations
import math
import numpy as np
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass


# ---------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------

def weighted_mean(x: np.ndarray, err: Optional[np.ndarray] = None) -> float:
    x = np.asarray(x, float)
    if err is None:
        return float(np.mean(x))
    w = 1.0 / (np.asarray(err, float) ** 2)
    return float(np.sum(w * x) / np.sum(w))


def wrms(x: np.ndarray, err: Optional[np.ndarray] = None, bias: Optional[float] = None) -> float:
    x = np.asarray(x, float)
    if err is None:
        mu = np.mean(x) if bias is None else bias
        return float(np.sqrt(np.mean((x - mu) ** 2)))
    w = 1.0 / (np.asarray(err, float) ** 2)
    mu = (np.sum(w * x) / np.sum(w)) if bias is None else bias
    num = np.sum(w * (x - mu) ** 2)
    den = np.sum(w)
    return float(np.sqrt(num / den))


def chi_squared(x: np.ndarray, err: np.ndarray, reduced: bool = False, dof: Optional[int] = None) -> float:
    z = np.asarray(x, float) / np.asarray(err, float)
    chi2 = float(np.dot(z, z))
    if reduced:
        if not dof or dof <= 0:
            raise ValueError("Reduced χ² requested but 'dof' not provided.")
        chi2 /= dof
    return chi2


def chi_squared_2d(x: np.ndarray, xerr: np.ndarray,
                   y: np.ndarray, yerr: np.ndarray,
                   xy_cor: Optional[np.ndarray] = None,
                   reduced: bool = False, dof: Optional[int] = None) -> float:
    nx = x / xerr
    ny = y / yerr
    if xy_cor is None:
        sep2 = nx**2 + ny**2
    else:
        rho = np.asarray(xy_cor, float)
        sep2 = (nx**2 + ny**2 - 2.0 * rho * nx * ny) / (1.0 - rho**2)
    chi2 = float(np.sum(sep2))
    if reduced:
        if not dof or dof <= 0:
            raise ValueError("Reduced χ² requested but 'dof' not provided.")
        chi2 /= dof
    return chi2


# --- chi-square tail prob (GOF) without hard SciPy dependency ---

def _gammaincc_cf(a, x, tol=1e-12, max_iter=10_000):
    """Regularized upper incomplete gamma Q(a, x) via Lentz's method (continued fraction).
    Accurate for x >= 0, a > 0. Used for chi-square GOF only."""
    if x <= 0:
        return 1.0
    # Lentz's algorithm for continued fraction of Q
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / max(b, tiny)
    h = d
    for i in range(1, max_iter + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < tol:
            break
    front = math.exp(-x + a * math.log(x) - math.lgamma(a))
    return front * h  # this is the (unnormalized) upper gamma / Gamma(a)


def goodness_of_fit(dof: int, chi2: float) -> float:
    """Right-tail probability P(Chi2_dof >= chi2)."""
    a = 0.5 * dof
    x = 0.5 * chi2
    return float(_gammaincc_cf(a, x))


# ---------------------------------------------------------------------
# Weighting (supports correlation OR covariance)
# ---------------------------------------------------------------------

def weight_matrix_corr(dra_err: np.ndarray, ddec_err: np.ndarray, rho: Optional[np.ndarray]) -> np.ndarray:
    """Build block-diagonal W = Cov^{-1} using correlation coefficients."""
    dra_err = np.asarray(dra_err, float)
    ddec_err = np.asarray(ddec_err, float)
    N = dra_err.size
    if rho is None:
        w_ra = 1.0 / (dra_err**2)
        w_dc = 1.0 / (ddec_err**2)
        return np.diag(np.concatenate([w_ra, w_dc]))
    # full inverse for each 2×2 block
    W = np.zeros((2*N, 2*N), float)
    for i in range(N):
        s1, s2, r = dra_err[i], ddec_err[i], float(rho[i])
        det = (s1**2)*(s2**2)*(1.0 - r**2)
        inv = (1.0/det) * np.array([[s2**2,  -r*s1*s2],
                                    [-r*s1*s2,  s1**2]])
        W[2*i:2*i+2, 2*i:2*i+2] = inv
    return W


def weight_matrix_cov(dra_err: np.ndarray, ddec_err: np.ndarray, cov: Optional[np.ndarray]) -> np.ndarray:
    """Build W from *covariance* (μas²) values per source."""
    dra_err = np.asarray(dra_err, float)
    ddec_err = np.asarray(ddec_err, float)
    N = dra_err.size
    W = np.zeros((2*N, 2*N), float)
    for i in range(N):
        s1, s2 = dra_err[i], ddec_err[i]
        c = 0.0 if cov is None else float(cov[i])
        Cov = np.array([[s1**2, c],
                        [c,     s2**2]])
        W[2*i:2*i+2, 2*i:2*i+2] = np.linalg.inv(Cov)
    return W


# ---------------------------------------------------------------------
# Forward model: degree-1 and degree-2
# (param order consistent with Jacobians below)
# ---------------------------------------------------------------------

def vsh_func01(ra: np.ndarray, dec: np.ndarray,
               g1: float, g2: float, g3: float,
               r1: float, r2: float, r3: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Degree-1 model (glide then rotation):
      dra  = -g1*sin(ra) + g2*cos(ra) - r1*cos(ra)*sin(dec) - r2*sin(ra)*sin(dec) + r3*cos(dec)
      ddec = -g1*cos(ra)*sin(dec) - g2*sin(ra)*sin(dec) + g3*cos(dec) + r1*sin(ra) - r2*cos(ra)
    """
    ra = np.asarray(ra, float)
    dec = np.asarray(dec, float)
    cra, sra = np.cos(ra), np.sin(ra)
    cdc, sdc = np.cos(dec), np.sin(dec)

    dra = -g1*sra + g2*cra - r1*cra*sdc - r2*sra*sdc + r3*cdc
    ddc = -g1*cra*sdc - g2*sra*sdc + g3*cdc + r1*sra - r2*cra
    return dra, ddc


def vsh_func02(ra: np.ndarray, dec: np.ndarray,
               ER_22: float, EI_22: float, ER_21: float, EI_21: float, E_20: float,
               MR_22: float, MI_22: float, MR_21: float, MI_21: float, M_20: float
               ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Degree-2 (E & M) terms, matching classic forms.
    """
    ra = np.asarray(ra, float)
    dec = np.asarray(dec, float)

    dra = (+ M_20 * np.sin(2*dec)
           - (MR_21*np.cos(ra) - MI_21*np.sin(ra)) * np.cos(2*dec)
           + (ER_21*np.sin(ra) + EI_21*np.cos(ra)) * np.sin(dec)
           - (MR_22*np.cos(2*ra) - MI_22*np.sin(2*ra)) * np.sin(2*dec)
           - 2*(ER_22*np.sin(2*ra) + EI_22*np.cos(2*ra)) * np.cos(dec))
    ddc = (+ E_20 * np.sin(2*dec)
           - (MR_21*np.sin(ra) + MI_21*np.cos(ra)) * np.sin(dec)
           - (ER_21*np.cos(ra) - EI_21*np.sin(ra)) * np.cos(2*dec)
           + 2*(MR_22*np.sin(2*ra) + MI_22*np.cos(2*ra)) * np.cos(dec)
           - (ER_22*np.cos(2*ra) - EI_22*np.sin(2*ra)) * np.sin(2*dec))
    return dra, ddc


def vsh_func(ra: np.ndarray, dec: np.ndarray,
             p: np.ndarray, l_max: int = 2) -> Tuple[np.ndarray, np.ndarray]:
    """Forward model wrapper using the unified parameter order."""
    if l_max == 1:
        return vsh_func01(ra, dec, *p[:6])
    elif l_max == 2:
        dra1, ddc1 = vsh_func01(ra, dec, *p[:6])
        dra2, ddc2 = vsh_func02(ra, dec, *p[6:])
        return dra1 + dra2, ddc1 + ddc2
    else:
        raise ValueError("l_max must be 1 or 2.")


# ---------------------------------------------------------------------
# Jacobians: degree-1 and degree-2 (rows stack RA then Dec)
# ---------------------------------------------------------------------

def jacobian_deg1(ra_rad: np.ndarray, dec_rad: np.ndarray, component: str = "full") -> np.ndarray:
    """
    Degree-1 Jacobian for params (g1,g2,g3,r1,r2,r3) or subset ('S' glide, 'T' rotation).
    Returns J with shape (2N, npar).
    """
    ra = np.asarray(ra_rad, float)
    dec = np.asarray(dec_rad, float)
    N = ra.size
    cra, sra = np.cos(ra), np.sin(ra)
    cdc, sdc = np.cos(dec), np.sin(dec)

    # order: g1,g2,g3,r1,r2,r3
    J_ra = np.column_stack([
        -sra,           # d(dra)/d(g1)
        cra,           # d(dra)/d(g2)
        np.zeros(N),   # d(dra)/d(g3)
        -cra*sdc,       # d(dra)/d(r1)
        -sra*sdc,       # d(dra)/d(r2)
        cdc            # d(dra)/d(r3)
    ])
    J_dc = np.column_stack([
        -cra*sdc,       # d(ddc)/d(g1)
        -sra*sdc,       # d(ddc)/d(g2)
        cdc,           # d(ddc)/d(g3)
        sra,           # d(ddc)/d(r1)
        -cra,           # d(ddc)/d(r2)
        np.zeros(N)    # d(ddc)/d(r3)
    ])

    if component.lower() == "t":
        cols = [3, 4, 5]
    elif component.lower() == "s":
        cols = [0, 1, 2]
    else:
        cols = [0, 1, 2, 3, 4, 5]

    return np.vstack([J_ra[:, cols], J_dc[:, cols]])


def jacobian_deg2(ra_rad: np.ndarray, dec_rad: np.ndarray) -> np.ndarray:
    """
    Degree-2 Jacobian (full 16-parameter set in the unified order):
      (g1,g2,g3, r1,r2,r3, ER_22, EI_22, ER_21, EI_21, E_20, MR_22, MI_22, MR_21, MI_21, M_20)

    Returns J with shape (2N, 16).
    """
    ra = np.asarray(ra_rad, float)
    dec = np.asarray(dec_rad, float)
    N = ra.size

    cra, sra = np.cos(ra), np.sin(ra)
    c2ra, s2ra = np.cos(2*ra), np.sin(2*ra)
    cdc, sdc = np.cos(dec), np.sin(dec)
    c2dc, s2dc = np.cos(2*dec), np.sin(2*dec)

    # degree-1 parts (as above)
    J1 = jacobian_deg1(ra, dec, component="full")  # (2N, 6)

    # degree-2 partials for dra
    par1_ER22 = -2 * s2ra * cdc
    par1_EI22 = -2 * c2ra * cdc
    par1_ER21 = sra * sdc
    par1_EI21 = cra * sdc
    par1_E20 = 0.0 * ra
    par1_MR22 = - s2dc * c2ra
    par1_MI22 = s2dc * s2ra
    par1_MR21 = - cra * c2dc
    par1_MI21 = sra * c2dc
    par1_M20 = s2dc

    # degree-2 partials for ddec
    par2_ER22 = par1_MI22
    par2_EI22 = par1_MR22
    par2_ER21 = par1_MI21
    par2_EI21 = par1_MR21
    par2_E20 = par1_M20
    par2_MR22 = -par1_EI22
    par2_MI22 = -par1_ER22
    par2_MR21 = -par1_EI21
    par2_MI21 = -par1_ER21
    par2_M20 = -par1_E20

    # stack RA/Dec rows into 10 degree-2 columns in correct order
    J2_ra = np.column_stack([par1_ER22, par1_EI22, par1_ER21, par1_EI21, par1_E20,
                             par1_MR22, par1_MI22, par1_MR21, par1_MI21, par1_M20])
    J2_dc = np.column_stack([par2_ER22, par2_EI22, par2_ER21, par2_EI21, par2_E20,
                             par2_MR22, par2_MI22, par2_MR21, par2_MI21, par2_M20])

    J2 = np.vstack([J2_ra, J2_dc])  # (2N, 10)

    # full order: [deg1(6)] + [deg2(10)]
    return np.concatenate([J1, J2], axis=1)


# ---------------------------------------------------------------------
# Normal equations & solve
# ---------------------------------------------------------------------

def normal_equations(J: np.ndarray, y: np.ndarray, W: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    JT = J.T
    A = JT @ W @ J
    b = JT @ W @ y
    return A, b


def solve_normal(A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Prefer Cholesky if SPD; else fall back to lstsq
    try:
        L = np.linalg.cholesky(A)
        y = np.linalg.solve(L, b)
        x = np.linalg.solve(L.T, y)
        # Cov = A^{-1} via Cholesky
        I = np.eye(A.shape[0])
        invL = np.linalg.solve(L, I)
        cov = invL.T @ invL
    except np.linalg.LinAlgError:
        x, *_ = np.linalg.lstsq(A, b, rcond=None)
        cov = np.linalg.pinv(A)

    sigma = np.sqrt(np.clip(np.diag(cov), 0.0, np.inf))
    with np.errstate(divide="ignore", invalid="ignore"):
        cor = cov / np.outer(sigma, sigma)
        cor[~np.isfinite(cor)] = 0.0
    return x, sigma, cor


# ---------------------------------------------------------------------
# Outliers
# ---------------------------------------------------------------------

def normalized_separation(dra: np.ndarray, ddec: np.ndarray,
                          dra_err: np.ndarray, ddec_err: np.ndarray,
                          rho: Optional[np.ndarray] = None) -> np.ndarray:
    nx = dra / dra_err
    ny = ddec / ddec_err
    if rho is None:
        return np.sqrt(nx**2 + ny**2)
    r = np.asarray(rho, float)
    val = (nx**2 + ny**2 - 2*r*nx*ny) / (1 - r**2)
    return np.sqrt(np.maximum(val, 0.0))


def sigma_clip_mask(dra_r: np.ndarray, ddec_r: np.ndarray,
                    dra_err: Optional[np.ndarray] = None,
                    ddec_err: Optional[np.ndarray] = None,
                    n: float = 3.0, weighted: bool = True) -> np.ndarray:
    if weighted and (dra_err is not None) and (ddec_err is not None):
        X = np.sqrt((dra_r/dra_err)**2 + (ddec_r/ddec_err)**2)
    else:
        X = np.sqrt(dra_r**2 + ddec_r**2)
    return X <= n


def rayleigh_clip_mask(dra_r: np.ndarray, ddec_r: np.ndarray,
                       dra_err: np.ndarray, ddec_err: np.ndarray,
                       rho: Optional[np.ndarray],
                       factor: float = 3.0) -> np.ndarray:
    X = normalized_separation(dra_r, ddec_r, dra_err, ddec_err, rho)
    thr = factor * np.median(X)
    return X <= thr


# ---------------------------------------------------------------------
# Fit API
# ---------------------------------------------------------------------

@dataclass
class FitResult:
    params: np.ndarray
    sigma: np.ndarray
    cor: np.ndarray
    residuals: Tuple[np.ndarray, np.ndarray]
    mask: np.ndarray
    stats_prefit: Dict[str, float]
    stats_postfit: Dict[str, float]


def _fit_core(dra: np.ndarray, ddec: np.ndarray,
              dra_err: np.ndarray, ddec_err: np.ndarray,
              ra_deg: np.ndarray, dec_deg: np.ndarray,
              l_max: int = 1,
              rho: Optional[np.ndarray] = None,
              cov: Optional[np.ndarray] = None,
              elimination: Optional[str] = None,
              threshold: float = 3.0) -> FitResult:

    ra = np.deg2rad(np.asarray(ra_deg, float))
    dec = np.deg2rad(np.asarray(dec_deg, float))
    dra = np.asarray(dra, float)
    ddec = np.asarray(ddec, float)
    dra_err = np.asarray(dra_err, float)
    ddec_err = np.asarray(ddec_err, float)

    N = dra.size
    P = 6 if l_max == 1 else 16
    dof = 2*N - P

    # prefit stats
    stats_pre = {
        "dra_bias": weighted_mean(dra, dra_err),
        "ddec_bias": weighted_mean(ddec, ddec_err),
        "dra_wrms": wrms(dra, dra_err),
        "ddec_wrms": wrms(ddec, ddec_err),
        "chi2": chi_squared_2d(dra, dra_err, ddec, ddec_err, rho, reduced=False)
    }
    stats_pre["reduced_chi2"] = stats_pre["chi2"] / max(dof, 1)
    stats_pre["gof"] = goodness_of_fit(max(dof, 1), stats_pre["chi2"])

    # design matrix
    if l_max == 1:
        J = jacobian_deg1(ra, dec, component="full")
    elif l_max == 2:
        J = jacobian_deg2(ra, dec)
    else:
        raise ValueError("l_max must be 1 or 2.")

    # weights
    y = np.concatenate([dra, ddec])
    if cov is not None:
        W = weight_matrix_cov(dra_err, ddec_err, cov)
    else:
        W = weight_matrix_corr(dra_err, ddec_err, rho)

    # first solve
    A, b = normal_equations(J, y, W)
    x, s, cor = solve_normal(A, b)

    # residuals
    yfit = J @ x
    rra = dra - yfit[:N]
    rdc = ddec - yfit[N:]

    # optional outlier handling
    mask = np.ones(N, dtype=bool)
    if elimination:
        elim = elimination.lower()
        if elim == "sigma":
            good = sigma_clip_mask(
                rra, rdc, dra_err, ddec_err, n=threshold, weighted=True)
        elif elim == "rayleigh":
            good = rayleigh_clip_mask(
                rra, rdc, dra_err, ddec_err, rho, factor=threshold)
        else:
            raise ValueError(
                "elimination must be one of: None, 'sigma', 'rayleigh'")

        mask = good
        # refit on clean sample
        dra1, ddc1 = dra[good], ddec[good]
        ra1, dec1 = ra[good], dec[good]
        drae1, ddce1 = dra_err[good], ddec_err[good]
        rho1 = None if rho is None else rho[good]
        cov1 = None if cov is None else cov[good]

        if l_max == 1:
            Jc = jacobian_deg1(ra1, dec1, component="full")
        else:
            Jc = jacobian_deg2(ra1, dec1)

        yc = np.concatenate([dra1, ddc1])
        if cov1 is not None:
            Wc = weight_matrix_cov(drae1, ddce1, cov1)
        else:
            Wc = weight_matrix_corr(drae1, ddce1, rho1)

        Ac, bc = normal_equations(Jc, yc, Wc)
        x, s, cor = solve_normal(Ac, bc)

        # residuals for all points with final params
        yfit_all = (jacobian_deg1(ra, dec, "full") if l_max ==
                    1 else jacobian_deg2(ra, dec)) @ x
        rra = dra - yfit_all[:N]
        rdc = ddec - yfit_all[N:]

    # postfit stats
    # after computing rra, rdc and before building stats_post
    N_used = int(mask.sum()) if mask is not None else N
    P = 6 if l_max == 1 else 16
    dof_post = max(2 * N_used - P, 1)

    chi2_post = chi_squared_2d(rra, dra_err, rdc, ddec_err, rho, reduced=False)
    stats_post = {
        "dra_bias": weighted_mean(rra, dra_err),
        "ddec_bias": weighted_mean(rdc, ddec_err),
        "dra_wrms": wrms(rra, dra_err),
        "ddec_wrms": wrms(rdc, ddec_err),
        "chi2": chi2_post,
        "reduced_chi2": chi2_post / dof_post,
        "gof": goodness_of_fit(dof_post, chi2_post),
    }

    return FitResult(
        params=x, sigma=s, cor=cor,
        residuals=(rra, rdc), mask=mask,
        stats_prefit=stats_pre, stats_postfit=stats_post
    )


def fit_deg1(dra: np.ndarray, ddec: np.ndarray,
             dra_err: np.ndarray, ddec_err: np.ndarray,
             ra_deg: np.ndarray, dec_deg: np.ndarray,
             rho: Optional[np.ndarray] = None, cov: Optional[np.ndarray] = None,
             elimination: Optional[str] = None, threshold: float = 3.0) -> FitResult:
    """Degree-1 fit (returns params in order: g1,g2,g3,r1,r2,r3)."""
    return _fit_core(dra, ddec, dra_err, ddec_err, ra_deg, dec_deg,
                     l_max=1, rho=rho, cov=cov,
                     elimination=elimination, threshold=threshold)


def fit_deg2(dra: np.ndarray, ddec: np.ndarray,
             dra_err: np.ndarray, ddec_err: np.ndarray,
             ra_deg: np.ndarray, dec_deg: np.ndarray,
             rho: Optional[np.ndarray] = None, cov: Optional[np.ndarray] = None,
             elimination: Optional[str] = None, threshold: float = 3.0) -> FitResult:
    """Degree-2 fit (returns params in unified 16-element order)."""
    return _fit_core(dra, ddec, dra_err, ddec_err, ra_deg, dec_deg,
                     l_max=2, rho=rho, cov=cov,
                     elimination=elimination, threshold=threshold)


# ====== minimal legacy-style helpers & runner (compact) ======


def _ga_hat():
    """Unit vector toward GC (ICRS) used across your legacy runs."""
    ra, dec = np.deg2rad(266.4), np.deg2rad(-28.9)
    return np.array([np.cos(ra)*np.cos(dec), np.sin(ra)*np.cos(dec), np.sin(dec)])


def _amp_ra_dec(v):
    """Return (amplitude, RA_deg, Dec_deg) for a 3-vector."""
    a = float(np.linalg.norm(v))
    RA = np.rad2deg(np.arctan2(v[1], v[0]))
    RA = RA if RA >= 0 else RA + 360.0
    DC = np.rad2deg(np.arctan2(v[2], np.hypot(v[0], v[1])))
    return a, RA, DC


def filter_by_cuts(pos_offset, X_max=4.1, ang_sep_max=10.0, fh=None):
    """
    Apply simple cuts; pos_offset is the 13-field legacy pack:
      [sou, RAdeg, DEdeg, dRA, e_dRA, dDE, e_dDE, cov, ang_sep, X_a, X_d, X, flg]
    """
    [sou, RAdeg, DEdeg, dRA, e_dRA, dDE, e_dDE,
        cov, ang_sep, X_a, X_d, X, flg] = pos_offset
    mask = np.ones_like(RAdeg, dtype=bool)
    if X_max is not None:
        mask &= (X <= X_max)
    if ang_sep_max is not None:
        mask &= (ang_sep <= ang_sep_max)
    if fh is not None:
        bad = ~mask
        print(
            f"## Outliers removed: {np.count_nonzero(bad)}  (X_max={X_max}, ang_sep_max={ang_sep_max})", file=fh)
    return [arr[mask] if arr is not None else None
            for arr in [sou, RAdeg, DEdeg, dRA, e_dRA, dDE, e_dDE, cov, ang_sep, X_a, X_d, X, flg]], mask


def _report_deg1(fit, fh, tag="deg1"):
    """Tiny, grep-friendly printout (assumes param order: g1,g2,g3,r1,r2,r3)."""
    p, s = fit.params, fit.sigma
    g, r = p[:3], p[3:6]
    gA, gRA, gDC = _amp_ra_dec(g)
    rA, rRA, rDC = _amp_ra_dec(r)
    print(f"#### {tag}: N_used={np.count_nonzero(fit.mask)}", file=fh)
    print(f"## Glide:   {g[0]:+6.1f}±{s[0]:4.1f} {g[1]:+6.1f}±{s[1]:4.1f} {g[2]:+6.1f}±{s[2]:4.1f}  => {gA:5.1f}  apex({gRA:.1f}°, {gDC:+.1f}°)", file=fh)
    print(f"## Rot:     {r[0]:+6.1f}±{s[3]:4.1f} {r[1]:+6.1f}±{s[4]:4.1f} {r[2]:+6.1f}±{s[5]:4.1f}  => {rA:5.1f}  apex({rRA:.1f}°, {rDC:+.1f}°)", file=fh)
    st = fit.stats_postfit
    print(
        f"## Stats: WRMS(dRA)={st['dra_wrms']:.2f}  WRMS(dDec)={st['ddec_wrms']:.2f}  chi2={st['chi2']:.1f}  chi2_red={st['reduced_chi2']:.2f}  GOF={st['gof']:.3f}", file=fh)
    # GA vs non-GA glide
    G_GA = float(np.dot(g, _ga_hat()))
    g_non = g - G_GA * _ga_hat()
    G_non, RA_non, DC_non = _amp_ra_dec(g_non)
    print(
        f"## Glide GA={G_GA:+5.1f}  non-GA={G_non:5.1f}  apex(non-GA)=({RA_non:.1f}°, {DC_non:+.1f}°)", file=fh)
    if fit.params.size >= 16:
        q = fit.params[6:]
        qs = fit.sigma[6:]
        print(
            f"## Quad (E/M): ER22={q[0]:+.1f}±{qs[0]:.1f} EI22={q[1]:+.1f}±{qs[1]:.1f} ...", file=fh)


def run_legacy(pos_offset,
               do_deg2=True,
               elim_mode=None,     # None | "sigma" | "rayleigh"
               elim_thr=3.0,
               use_cov=True,
               X_max=4.1, ang_sep_max=10.0,
               log_handle=None):
    """
    One-call legacy-style pipeline that uses the unified solvers (fit_deg1/fit_deg2).
    Returns: {"deg1": FitResult, "deg2": FitResult|None, "mask": mask_used}
    """
    fh = log_handle
    pos_offset, pre_mask = filter_by_cuts(pos_offset, X_max, ang_sep_max, fh)
    [sou, RAdeg, DEdeg, dRA, e_dRA, dDE, e_dDE, cov, _, _, _, _, _] = pos_offset

    fit1 = fit_deg1(dRA, dDE, e_dRA, e_dDE, RAdeg, DEdeg,
                    rho=None if use_cov else None,
                    cov=cov if use_cov else None,
                    elimination=elim_mode, threshold=elim_thr)
    if fh:
        _report_deg1(fit1, fh, "deg1")

    out = {"deg1": fit1, "deg2": None, "mask": pre_mask & fit1.mask}
    if do_deg2:
        fit2 = fit_deg2(dRA, dDE, e_dRA, e_dDE, RAdeg, DEdeg,
                        rho=None if use_cov else None,
                        cov=cov if use_cov else None,
                        elimination=elim_mode, threshold=elim_thr)
        if fh:
            _report_deg1(fit2, fh, "deg2 (dipole subset)")
        out["deg2"] = fit2
        out["mask"] = pre_mask & fit2.mask  # last-stage mask if you prefer

    return out
# ====== end compact block ======


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

__all__ = [
    # stats
    "weighted_mean", "wrms", "chi_squared", "chi_squared_2d", "goodness_of_fit",
    # model
    "vsh_func01", "vsh_func02", "vsh_func",
    # jacobians
    "jacobian_deg1", "jacobian_deg2",
    # weighting
    "weight_matrix_corr", "weight_matrix_cov",
    # solve
    "normal_equations", "solve_normal",
    # outliers
    "normalized_separation", "sigma_clip_mask", "rayleigh_clip_mask",
    # fits
    "FitResult", "fit_deg1", "fit_deg2",
    "run_legacy", "filter_by_cuts"
]


# ====================== Synthetic data & self-tests ======================

def _synth_catalog(N=500, seed=42, l_max=1, use_cov=True, noise=1.0):
    """
    Generate a synthetic catalog with known VSH parameters.
    Returns (dra, ddec, dra_err, ddec_err, ra_deg, dec_deg, rho, cov, true_params)
    """
    rng = np.random.default_rng(seed)
    # sky positions (uniform in RA, sin-uniform in Dec)
    ra = rng.uniform(0, 360, N)
    z = rng.uniform(-1, 1, N)  # sin(dec)
    dec = np.rad2deg(np.arcsin(z))

    # true parameters (in the same order as the solvers expect)
    # ~typical glide amplitude values
    g_true = np.array([+5.0, -6.0, -3.0])
    r_true = np.array([+1.0, +2.0, -1.0])        # small rotation
    if l_max == 1:
        p_true = np.concatenate([g_true, r_true])
    else:
        quad_true = np.array([  # 10 quadrupole terms
            +1.0, -0.8, +2.2, -0.5, +1.1,   # ER22, EI22, ER21, EI21, E20
            +0.7, -0.2, -1.1, +0.9, +0.3    # MR22, MI22, MR21, MI21, M20
        ])
        p_true = np.concatenate([g_true, r_true, quad_true])

    # noiseless model
    dra0, ddc0 = vsh_func(np.deg2rad(ra), np.deg2rad(dec), p_true, l_max=l_max)

    # errors & correlations
    dra_err = noise * (0.6 + 0.4 * rng.random(N))   # heterogeneous errors
    ddc_err = noise * (0.6 + 0.4 * rng.random(N))
    if use_cov:
        rho = rng.uniform(-0.3, 0.3, N)
        cov = rho * dra_err * ddc_err
    else:
        rho, cov = None, None

    # draw correlated noise per source
    dra = np.empty(N)
    ddec = np.empty(N)
    for i in range(N):
        if use_cov:
            C = np.array([[dra_err[i]**2, cov[i]],
                          [cov[i],        ddc_err[i]**2]])
            e = rng.multivariate_normal(mean=[0.0, 0.0], cov=C)
        else:
            e = np.array([rng.normal(0, dra_err[i]),
                         rng.normal(0, ddc_err[i])])
        dra[i] = dra0[i] + e[0]
        ddec[i] = ddc0[i] + e[1]

    return dra, ddec, dra_err, ddc_err, ra, dec, rho, cov, p_true


def _assert_close(est, true, tol=3.5):
    """Check |est-true| <= tol*sigma elementwise; return boolean mask."""
    sigma = tol  # if you pass vectors, adapt as needed
    return np.all(np.isfinite(est)) and np.all(np.abs(est - true) <= tol)


def _self_test(verbose=True):
    """
    Quick smoke tests for deg1/deg2 with/without covariance and optional clipping.
    Prints a tiny summary and returns True/False.
    """
    OK = True

    for lmax in (1, 2):
        for use_cov in (False, True):
            dra, ddc, dre, dde, ra, dec, rho, cov, p_true = _synth_catalog(
                N=1200, l_max=lmax, use_cov=use_cov, noise=1.0, seed=1234 + 97*lmax + (31 if use_cov else 0)
            )

            # No clipping
            fit = (fit_deg1 if lmax == 1 else fit_deg2)(
                dra, ddc, dre, dde, ra, dec,
                rho=None if use_cov else None,
                cov=cov if use_cov else None,
                elimination=None
            )

            # Simple parameter check on the dipole block
            dip_est = fit.params[:6]
            dip_true = p_true[:6]
            ok_block = np.all(np.isfinite(dip_est)) and np.linalg.norm(
                dip_est - dip_true) < 5.0
            OK &= bool(ok_block)

            # With sigma clip (should be stable)
            fit_clip = (fit_deg1 if lmax == 1 else fit_deg2)(
                dra, ddc, dre, dde, ra, dec,
                rho=None if use_cov else None,
                cov=cov if use_cov else None,
                elimination="sigma", threshold=3.5
            )
            ok_clip = np.all(np.isfinite(fit_clip.params[:6]))
            OK &= bool(ok_clip)

            if verbose:
                tag = f"deg{lmax} {'cov' if use_cov else 'diag'}"
                gA, gRA, gDC = _amp_ra_dec(fit.params[:3])
                print(
                    f"[{tag}] N_used={fit.mask.sum():4d}  |g|≈{gA:5.2f}  chi2_red={fit.stats_postfit['reduced_chi2']:.2f}")

    if verbose:
        print("SELF-TEST:", "PASS" if OK else "FAIL")
    return OK


if __name__ == "__main__":
    _self_test()
