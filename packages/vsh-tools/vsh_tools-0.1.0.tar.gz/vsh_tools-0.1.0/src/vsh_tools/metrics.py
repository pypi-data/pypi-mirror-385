#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: metrics.py
"""
Fit diagnostics:
- pre/post residual summaries (bias, WRMS, RSE)
- normalized residuals stats
- chi-square, reduced chi-square, goodness-of-fit
"""

from __future__ import annotations

import numpy as np
from .stats import (
    calc_mean,
    calc_wrms,
    calc_rse,
    calc_chi2_2d,
    calc_gof,
)

__all__ = ["residual_stats_calc", "print_stats_info"]


def residual_stats_calc(dra, ddc, dra_err, ddc_err, ra_dc_cor, num_dof):
    """
    Calculate statistics for residuals.

    Parameters
    ----------
    dra, ddc : array_like
        Tangential components (Δα⋅cosδ, Δδ).
    dra_err, ddc_err : array_like
        Formal uncertainties for each component.
    ra_dc_cor : array_like or None
        Correlation coefficient between dra and ddc.
    num_dof : int
        Degrees of freedom.

    Returns
    -------
    stats : dict
        Keys include dra_bias, ddec_bias, dra_wrms, ddec_wrms, dra_rse, ddec_rse,
        nor_dra_bias, nor_ddec_bias, nor_dra_std, nor_ddec_std,
        nor_dra_rse, nor_ddec_rse, chi2, reduced_chi2, gof.
    """
    dra = np.asarray(dra, dtype=float)
    ddc = np.asarray(ddc, dtype=float)
    dra_err = np.asarray(dra_err, dtype=float)
    ddc_err = np.asarray(ddc_err, dtype=float)

    if not (dra.shape == ddc.shape == dra_err.shape == ddc_err.shape):
        raise ValueError(
            "dra, ddc, dra_err, ddc_err must have the same shape.")

    stats = {}

    # Bias (weighted means)
    stats["dra_bias"] = calc_mean(dra, dra_err)
    stats["ddec_bias"] = calc_mean(ddc, ddc_err)

    # WRMS about the (weighted) bias
    stats["dra_wrms"] = calc_wrms(dra, dra_err, stats["dra_bias"])
    stats["ddec_wrms"] = calc_wrms(
        ddc, ddc_err, stats["ddec_bias"])  # fixed bug

    # Robust scatter estimates
    stats["dra_rse"] = calc_rse(dra)
    stats["ddec_rse"] = calc_rse(ddc)

    # Normalized residuals
    with np.errstate(divide="ignore", invalid="ignore"):
        nor_dra = dra / dra_err
        nor_ddc = ddc / ddc_err
        nor_dra[~np.isfinite(nor_dra)] = 0.0
        nor_ddc[~np.isfinite(nor_ddc)] = 0.0

    # Bias, std, RSE of normalized residuals
    stats["nor_dra_bias"] = calc_mean(nor_dra)
    stats["nor_ddec_bias"] = calc_mean(nor_ddc)
    stats["nor_dra_std"] = calc_wrms(nor_dra)
    stats["nor_ddec_std"] = calc_wrms(nor_ddc)
    stats["nor_dra_rse"] = calc_rse(nor_dra)
    stats["nor_ddec_rse"] = calc_rse(nor_ddc)

    # Chi-square (2D) and GOF
    stats["chi2"] = calc_chi2_2d(dra, dra_err, ddc, ddc_err, ra_dc_cor)
    stats["reduced_chi2"] = stats["chi2"] / float(num_dof)
    stats["gof"] = calc_gof(int(num_dof), stats["chi2"])

    return stats


def print_stats_info(apr_stats, pos_stats):
    """
    Pretty-print pre-/post-fit statistics side-by-side.

    Parameters
    ----------
    apr_stats, pos_stats : dict
        As returned by residual_stats_calc.
    """
    print("")
    print("Statistics information")
    print("-------------------------------------------------------------------")
    print("             Pre-fit             |             Post-fit            ")
    print("-------------------------------------------------------------------")
    print("         dRA*         dDec       |         dRA*         dDec       ")
    print(
        "Bias  {:7.1f}      {:7.1f}       |      {:7.1f}      {:7.1f}".format(
            apr_stats["dra_bias"], apr_stats["ddec_bias"],
            pos_stats["dra_bias"], pos_stats["ddec_bias"],
        )
    )
    print(
        "WRMS  {:7.1f}      {:7.1f}       |      {:7.1f}      {:7.1f}".format(
            apr_stats["dra_wrms"], apr_stats["ddec_wrms"],
            pos_stats["dra_wrms"], pos_stats["ddec_wrms"],
        )
    )
    print(
        "RSE   {:7.1f}      {:7.1f}       |      {:7.1f}      {:7.1f}".format(
            apr_stats["dra_rse"], apr_stats["ddec_rse"],
            pos_stats["dra_rse"], pos_stats["ddec_rse"],
        )
    )
    print("-------------------------------------------------------------------")
    print("    Nor. dRA*    Nor. dDec       |    Nor. dRA*    Nor. dDec       ")
    print("-------------------------------------------------------------------")
    print("         dRA*         dDec       |         dRA*         dDec       ")
    print(
        "Bias  {:7.1f}      {:7.1f}       |      {:7.1f}      {:7.1f}".format(
            apr_stats["nor_dra_bias"], apr_stats["nor_ddec_bias"],
            pos_stats["nor_dra_bias"], pos_stats["nor_ddec_bias"],
        )
    )
    print(
        "Std   {:7.1f}      {:7.1f}       |      {:7.1f}      {:7.1f}".format(
            apr_stats["nor_dra_std"], apr_stats["nor_ddec_std"],
            pos_stats["nor_dra_std"], pos_stats["nor_ddec_std"],
        )
    )
    print(
        "RSE   {:7.1f}      {:7.1f}       |      {:7.1f}      {:7.1f}".format(
            apr_stats["nor_dra_rse"], apr_stats["nor_ddec_rse"],
            pos_stats["nor_dra_rse"], pos_stats["nor_ddec_rse"],
        )
    )
    print("-------------------------------------------------------------------")
    print(
        "Chi-Square       {:9.1f}       |                 {:9.1f}".format(
            apr_stats["chi2"], pos_stats["chi2"]
        )
    )
    print(
        "Red. Chi-square  {:9.1f}       |                 {:9.1f}".format(
            apr_stats["reduced_chi2"], pos_stats["reduced_chi2"]
        )
    )
    print(
        "Good-of-fitness  {:9.1f}       |                 {:9.1f}".format(
            apr_stats["gof"], pos_stats["gof"]
        )
    )
    print("-------------------------------------------------------------------")
    print("")
