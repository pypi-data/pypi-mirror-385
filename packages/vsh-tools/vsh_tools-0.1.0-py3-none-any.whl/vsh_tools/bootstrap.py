#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: bootstrap.py
"""
Nonparametric bootstrap for VSH parameter uncertainties.
"""

from __future__ import annotations

import numpy as np

from .outliers import extract_data
from .linalg import nor_eq_sol
from .transforms import convert_ts_to_rgq


# ----------------------------- utilities -----------------------------
def bs_freq(x_or_n=None) -> int:
    """
    Bootstrap resampling frequency N ≈ n * ln(n)^2.

    Accepts either an array (length n) or an integer n.
    Falls back to N=1000 if None given.
    """
    print("Decide the frequency of bootstrap resamplings")
    if x_or_n is None:
        print("Since no sample is given, using the default value (1000).")
        return 1000

    n = int(x_or_n if np.isscalar(x_or_n) else len(x_or_n))
    if n <= 1:
        return 1000
    N = int(n * (np.log(n) ** 2))
    print(f"Sample size n={n}, resampling frequency N ≈ n * ln(n)^2 = {N}")
    return max(N, 1)


def bs_formal_error(x, xi):
    """
    Estimate mean, std of bootstrap draws, and RMS around the original x.
    """
    xi = np.asarray(xi, dtype=float)
    xi_mean = float(np.mean(xi))
    xi_std = float(np.std(xi, ddof=1)) if xi.size > 1 else 0.0
    denom = max(xi.size - 1, 1)
    xi_rms = float(np.sqrt(np.sum((xi - x) ** 2) / denom))
    return xi_mean, xi_std, xi_rms


def bs_resampling(X, Y, samp_size=None):
    """
    Bootstrap resample paired arrays X, Y with replacement.
    """
    X = np.asarray(X)
    Y = np.asarray(Y)
    if X.shape[0] != Y.shape[0]:
        raise ValueError("X and Y must have the same length.")
    n = X.shape[0]
    m = int(n if samp_size is None else samp_size)
    idx = np.random.choice(n, size=m, replace=True)
    return X[idx], Y[idx]


def bs_resampling_indx(X, samp_size=None):
    """
    Return bootstrap indices for X (size given or len(X)), with replacement.
    """
    n = len(X)
    m = int(n if samp_size is None else samp_size)
    return np.random.choice(n, size=m, replace=True)


# ----------------------------- main -----------------------------
def bootstrap_resample_4_err(
    mask,
    dra,
    ddc,
    dra_err,
    ddc_err,
    ra_rad,
    dc_rad,
    ra_dc_cor,
    l_max,
    fit_type,
    num_iter,
    output,
):
    """
    Estimate formal uncertainty via nonparametric bootstrap.

    Returns
    -------
    output : dict
        Updated with bootstrap summaries for VSH coeffs and RGQ terms.
    """
    # Clean sample (if a mask was applied)
    if not np.all(mask):
        dra, ddc, dra_err, ddc_err, ra_rad, dc_rad, ra_dc_cor = extract_data(
            mask, dra, ddc, dra_err, ddc_err, ra_rad, dc_rad, ra_dc_cor
        )

    # Current estimates (baseline)
    pmt = np.asarray(output["pmt"])
    if "pmt1" in output:
        pmt1 = np.asarray(output["pmt1"])
        degree_key = "pmt1"
    else:
        pmt1 = np.asarray(output["pmt2"])
        degree_key = "pmt2"

    # Bootstrap sizes
    N_samp = len(dra)
    N_resamp = bs_freq(N_samp)
    N_pmt = pmt.size
    N_pmt1 = pmt1.size

    pmt_ts_array = np.zeros((N_resamp, N_pmt))    # VSH coeffs
    # RGQ terms (length depends on l_max & fit_type)
    pmt_rgq_array = np.zeros((N_resamp, N_pmt1))

    for i in range(N_resamp):
        # Indices for a bootstrap sample
        new_idx = bs_resampling_indx(dra)

        # Slice all arrays consistently (extract_data accepts index arrays too)
        dra1, ddc1, dra_err1, ddc_err1, ra_rad1, dc_rad1, ra_dc_cor1 = extract_data(
            new_idx, dra, ddc, dra_err, ddc_err, ra_rad, dc_rad, ra_dc_cor
        )

        # Refit on the resampled data
        pmti, sigi, cor_mati, _, _ = nor_eq_sol(
            dra1, ddc1, dra_err1, ddc_err1, ra_rad1, dc_rad1,
            ra_dc_cor=ra_dc_cor1, l_max=l_max, fit_type=fit_type,
            num_iter=num_iter, calc_res=True
        )
        pmt_ts_array[i, :] = pmti

        # Convert to rotation/glide/quadrupolar terms
        conv = convert_ts_to_rgq(pmti, sigi, cor_mati, l_max, fit_type)
        rgq = np.asarray(conv["pmt1"] if "pmt1" in conv else conv["pmt2"])
        if rgq.size != N_pmt1:
            # If the pipeline later changes lengths, keep it robust:
            rgq = rgq[:N_pmt1]
        pmt_rgq_array[i, :] = rgq

    # Bootstrap summaries for VSH coeffs
    pmt_ts_mean = np.zeros(N_pmt)
    pmt_ts_std = np.zeros(N_pmt)
    pmt_ts_rms = np.zeros(N_pmt)
    for i in range(N_pmt):
        meani, stdi, rmsi = bs_formal_error(pmt[i], pmt_ts_array[:, i])
        pmt_ts_mean[i], pmt_ts_std[i], pmt_ts_rms[i] = meani, stdi, rmsi

    # Bootstrap summaries for RGQ terms
    pmt_rgq_mean = np.zeros(N_pmt1)
    pmt_rgq_std = np.zeros(N_pmt1)
    pmt_rgq_rms = np.zeros(N_pmt1)
    for i in range(N_pmt1):
        meani, stdi, rmsi = bs_formal_error(pmt1[i], pmt_rgq_array[:, i])
        pmt_rgq_mean[i], pmt_rgq_std[i], pmt_rgq_rms[i] = meani, stdi, rmsi

    # Store results
    output["pmt_bs_mean"] = pmt_ts_mean
    output["pmt_bs_std"] = pmt_ts_std
    output["pmt_bs_rms"] = pmt_ts_rms

    output[f"{degree_key}_bs_mean"] = pmt_rgq_mean
    output[f"{degree_key}_bs_std"] = pmt_rgq_std
    output[f"{degree_key}_bs_rms"] = pmt_rgq_rms

    # Notes (keep as a list; caller can print if needed)
    output["note"] = output.get("note", []) + [
        "pmt_bs_mean/std/rms: VSH coefficients from bootstrap sampling",
        f"{degree_key}_bs_mean/std/rms: glide+rotation(+quadrupolar) from bootstrap sampling",
    ]

    return output


def main():
    print("Have a nice day!")


if __name__ == "__main__":
    main()
