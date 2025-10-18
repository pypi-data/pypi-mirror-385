#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: outliers.py
"""
Auto- and standard-elimination wrappers around VSH least-squares.
"""

from __future__ import annotations

import numpy as np

# Stats / Linalg
from .stats import calc_nor_sep
from .linalg import (
    nor_eq_sol_from_cache,
    nor_eq_sol,
    residual_calc_from_cache,
    cache_mat_calc,
    rm_cache_mat,
)

__all__ = [
    "extract_data",
    "elim_on_nor_sep",
    "auto_elim_vsh_fit",
    "std_elim_vsh_fit",
]


# ----------------------------- helpers -----------------------------
def extract_data(mask, dra, ddc, dra_err, ddc_err, ra_rad, dc_rad, ra_dc_cor=None):
    """Slice arrays with a boolean mask and keep correlation in sync."""
    dra_new, ddc_new = dra[mask], ddc[mask]
    dra_err_new, ddc_err_new = dra_err[mask], ddc_err[mask]
    ra_rad_new, dc_rad_new = ra_rad[mask], dc_rad[mask]

    if ra_dc_cor is None:
        ra_dc_cor_new = None
    else:
        ra_dc_cor_new = ra_dc_cor[mask]

    return dra_new, ddc_new, dra_err_new, ddc_err_new, ra_rad_new, dc_rad_new, ra_dc_cor_new


def elim_on_nor_sep(clip_limit, dra, ddc, dra_err, ddc_err, ra_dc_cor=None):
    """Build a mask by clipping on normalized separation."""
    nor_sep = calc_nor_sep(dra, dra_err, ddc, ddc_err, ra_dc_cor)
    med_nor_sep = np.median(nor_sep)
    max_nor_sep = float(clip_limit) * med_nor_sep
    mask = (nor_sep <= max_nor_sep)
    return max_nor_sep, mask


# ----------------------------- main routines -----------------------------
def auto_elim_vsh_fit(
    clip_limit,
    dra,
    ddc,
    dra_err,
    ddc_err,
    ra_rad,
    dc_rad,
    ra_dc_cor=None,
    l_max=1,
    fit_type="full",
    num_iter=100,
):
    """
    Iterative fit with auto-elimination based on normalized separation.

    Returns
    -------
    pmt, sig, cor_mat, dra_r, ddc_r, mask
    """
    print("==================== Auto-elimination ====================")
    print("    Nb_iteration    Nb_sources    Nb_outliers    Threshold")
    print("    {:11d}    {:9d}    {:9d}    {:9.3f}".format(
        0, len(dra), 0, 0.0))

    mask1 = np.full(len(dra), True, dtype=bool)
    iter_count = 0

    # First elimination on raw residuals
    max_nor_sep2, mask2 = elim_on_nor_sep(
        clip_limit, dra, ddc, dra_err, ddc_err, ra_dc_cor)

    # Cache matrices once for speed
    suffix_array = cache_mat_calc(
        dra, ddc, dra_err, ddc_err, ra_rad, dc_rad,
        ra_dc_cor=ra_dc_cor, l_max=l_max, fit_type=fit_type, num_iter=num_iter
    )

    # Iterate until mask converges
    while np.any(mask1 != mask2):
        max_nor_sep1, mask1 = max_nor_sep2, mask2

        dra1, ddc1, dra_err1, ddc_err1, ra_rad1, dc_rad1, ra_dc_cor1 = extract_data(
            mask1, dra, ddc, dra_err, ddc_err, ra_rad, dc_rad, ra_dc_cor
        )

        iter_count += 1
        print(
            "    {:11d}    {:9d}    {:9d}    {:9.3f}".format(
                iter_count, len(dra1), len(dra) - len(dra1), max_nor_sep1
            )
        )

        # Fit on the current clean sample (no residuals needed here)
        pmt, sig, cor_mat = nor_eq_sol(
            dra1, ddc1, dra_err1, ddc_err1, ra_rad1, dc_rad1,
            ra_dc_cor=ra_dc_cor1, l_max=l_max, fit_type=fit_type,
            num_iter=num_iter, calc_res=False
        )

        # Residuals for all sources using cached Jacobians
        dra_r, ddc_r = residual_calc_from_cache(dra, ddc, pmt, suffix_array)

        # Recompute mask on normalized separation of residuals
        max_nor_sep2, mask2 = elim_on_nor_sep(
            clip_limit, dra_r, ddc_r, dra_err, ddc_err, ra_dc_cor)

    # Final outputs
    mask = mask1

    if iter_count == 0:
        # No elimination happened; just solve using cached blocks and get residuals
        pmt, sig, cor_mat, dra_r, ddc_r = nor_eq_sol_from_cache(
            dra, ddc, suffix_array, calc_res=True)
    else:
        # We already computed dra_r, ddc_r in the last loop
        pass

    # Clean cache
    rm_cache_mat(suffix_array)

    return pmt, sig, cor_mat, dra_r, ddc_r, mask


def std_elim_vsh_fit(
    x_limit,
    dra,
    ddc,
    dra_err,
    ddc_err,
    ra_rad,
    dc_rad,
    ra_dc_cor=None,
    l_max=1,
    fit_type="full",
    num_iter=100,
):
    """
    One-shot clip on normalized separation, then fit.

    Returns
    -------
    pmt, sig, cor_mat, dra_r, ddc_r, mask
    """
    # Cache matrices for residual prediction on the full set
    suffix_array = cache_mat_calc(
        dra, ddc, dra_err, ddc_err, ra_rad, dc_rad,
        ra_dc_cor=ra_dc_cor, l_max=l_max, fit_type=fit_type, num_iter=num_iter
    )

    # Build mask
    nor_sep = calc_nor_sep(dra, dra_err, ddc, ddc_err, ra_dc_cor)
    mask = (nor_sep <= float(x_limit))

    # Fit on the clean sample
    dra1, ddc1, dra_err1, ddc_err1, ra_rad1, dc_rad1, ra_dc_cor1 = extract_data(
        mask, dra, ddc, dra_err, ddc_err, ra_rad, dc_rad, ra_dc_cor
    )

    print("==================== Standard-elimination ====================")
    print("    Nb_sources    Nb_outliers    Threshold")
    print("    {:9d}    {:9d}    {:9.3f}".format(
        len(dra1), len(dra) - len(dra1), x_limit))

    pmt, sig, cor_mat = nor_eq_sol(
        dra1, ddc1, dra_err1, ddc_err1, ra_rad1, dc_rad1,
        ra_dc_cor=ra_dc_cor1, l_max=l_max, fit_type=fit_type,
        num_iter=num_iter, calc_res=False
    )

    # Residuals on full set using cached Jacobians
    dra_r, ddc_r = residual_calc_from_cache(dra, ddc, pmt, suffix_array)

    # Clean cache
    rm_cache_mat(suffix_array)

    return pmt, sig, cor_mat, dra_r, ddc_r, mask


def main():
    print("Have a nice day!")


if __name__ == "__main__":
    main()
