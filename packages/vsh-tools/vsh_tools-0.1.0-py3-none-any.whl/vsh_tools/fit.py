#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: fit.py
"""
Top-level VSH fitting routines:
- vsh_fit (core)
- convenience wrappers: rotgli_fit / rotgliquad_fit
- table-friendly wrappers
"""

from __future__ import annotations

import os
import sys
import numpy as np

# Local modules (renamed)
from .linalg import nor_eq_sol
from .significance import check_vsh_sig
from .diagnostics import prefit_check, prefit_info
from .metrics import print_stats_info, residual_stats_calc
from .outliers import auto_elim_vsh_fit, std_elim_vsh_fit
from .transforms import convert_ts_to_rgq, add_rgq_to_output
from .bootstrap import bootstrap_resample_4_err


# -----------------------------  MAIN -----------------------------
def vsh_fit(
    dra,
    ddc,
    dra_err,
    ddc_err,
    ra,
    dc,
    ra_dc_cor=None,
    l_max: int = 1,
    fit_type: str = "full",
    pos_in_rad: bool = False,
    num_iter: int = 100,
    **kwargs,
):
    """
    VSH fit to a tangential vector field.

    Parameters
    ----------
    dra, ddc : array_like
        Δα⋅cosδ, Δδ (same units, e.g. μas/yr).
    dra_err, ddc_err : array_like
        Formal uncertainties for dra, ddc.
    ra, dc : array_like
        Sky positions (deg unless pos_in_rad=True).
    ra_dc_cor : array_like or None
        Correlation coefficient between dra and ddc.
    l_max : int
        Maximum degree (>=1).
    fit_type : {"full","T","S"}
        Components to fit.
    pos_in_rad : bool
        If True, `ra`, `dc` are already in radians.
    num_iter : int
        Chunk size for block processing (~100 is fine).

    Keyword options
    ---------------
    std_clean : bool
        If True, one-shot clip on normalized separation using `x_limit`.
    x_limit : float
        Threshold X for std_clean (default: sqrt(2 ln N)).
    clip_limit : float
        If set, iterative auto-elimination using median(X)*clip_limit.
    print_stats : bool
        Print pre-/post-fit statistics.
    check_sig : bool
        Print degree-wise power/Z significance.
    bs_err : bool
        Bootstrap-rescale uncertainties (slow).
    verbose : bool
        If False, suppress printed logs.

    Returns
    -------
    output : dict
        Keys include: "pmt", "sig", "cor", "residual", and transformed RG(Q) terms.
    """
    if pos_in_rad:
        ra_rad, dc_rad = np.asarray(ra, float), np.asarray(dc, float)
    else:
        ra_rad = np.deg2rad(ra)
        dc_rad = np.deg2rad(dc)

    dra = np.asarray(dra, float)
    ddc = np.asarray(ddc, float)
    dra_err = np.asarray(dra_err, float)
    ddc_err = np.asarray(ddc_err, float)
    if not (dra.shape == ddc.shape == dra_err.shape == ddc_err.shape == ra_rad.shape == dc_rad.shape):
        raise ValueError(
            "dra, ddc, dra_err, ddc_err, ra, dc must all have the same shape.")

    num_sou = len(dra)
    num_pmt = 2 * l_max * (l_max + 2)
    prefit_check(num_sou, num_pmt)  # raises on failure

    # Per your original, leave the -1 term as-is
    num_dof = 2 * num_sou - num_pmt - 1

    # Setup optional quiet mode
    quiet = bool(kwargs.get("verbose") is False)
    if quiet:
        old_target = sys.stdout
        f = open(os.devnull, "w")
        sys.stdout = f

    # 1) header
    print("----------------------- VSH Fit (by Niu LIU) -----------------------")
    prefit_info(num_sou, num_pmt, num_dof, l_max)

    # 2) fitting + optional elimination
    if kwargs.get("std_clean", False):
        print("An upper limit will be put on the normalized separation X.")
        x_limit = kwargs.get("x_limit", None)
        if x_limit is None:
            x_limit = float(np.sqrt(2.0 * np.log(num_sou)))
            print("No x_limit given; using Rayleigh-predicted default sqrt(2 ln N).")
        elif not isinstance(x_limit, (int, float)):
            raise ValueError("Parameter 'x_limit' must be a number.")

        print(
            "The LSQ fit is performed on sources with normalized separation X <= {:.3f}.\n".format(
                x_limit
            )
        )
        pmt, sig, cor_mat, dra_r, ddc_r, mask = std_elim_vsh_fit(
            x_limit, dra, ddc, dra_err, ddc_err, ra_rad, dc_rad,
            ra_dc_cor=ra_dc_cor, l_max=l_max, fit_type=fit_type, num_iter=num_iter
        )

    elif kwargs.get("clip_limit", None) is not None:
        clip_limit = kwargs["clip_limit"]
        if not isinstance(clip_limit, (int, float)):
            raise ValueError("Parameter 'clip_limit' must be a number.")
        print(
            "Iterative fit with auto-elimination until convergence:\n"
            f"keep sources with X <= {clip_limit:.3f} * median(X).\n"
        )
        pmt, sig, cor_mat, dra_r, ddc_r, mask = auto_elim_vsh_fit(
            clip_limit, dra, ddc, dra_err, ddc_err, ra_rad, dc_rad,
            ra_dc_cor=ra_dc_cor, l_max=l_max, fit_type=fit_type, num_iter=num_iter
        )
    else:
        print("No constraint is put on the data; single LSQ fit.")
        pmt, sig, cor_mat, dra_r, ddc_r = nor_eq_sol(
            dra, ddc, dra_err, ddc_err, ra_rad, dc_rad,
            ra_dc_cor=ra_dc_cor, l_max=l_max, fit_type=fit_type, num_iter=num_iter
        )
        mask = np.full(num_sou, True, dtype=bool)

    # 3) statistics (pre/post)
    apr_stats = residual_stats_calc(
        dra, ddc, dra_err, ddc_err, ra_dc_cor, num_dof)
    pos_stats = residual_stats_calc(
        dra_r, ddc_r, dra_err, ddc_err, ra_dc_cor, num_dof)
    if kwargs.get("print_stats", False):
        print_stats_info(apr_stats, pos_stats)

    # 4) significance (optional)
    if kwargs.get("check_sig", False):
        check_vsh_sig(dra, ddc, pmt, sig, l_max, fit_type)

    # 5) assemble output
    output = {}
    output["note"] = [
        "pmt: fitted VSH parameters",
        "sig: formal uncertainties (rescaled below)",
        "cor: correlation coefficient matrix",
        "residual: post-fit residual of (dra, ddc)",
    ]
    output["pmt"] = pmt
    output["sig_lsq"] = sig
    output["cor"] = cor_mat
    output["residual"] = [dra_r, ddc_r]

    # 5.1 rescale formal uncertainties by reduced-chi2 of post-fit residuals
    sig = sig * np.sqrt(pos_stats["reduced_chi2"])
    output["sig"] = sig

    # 5.2 convert to rotation / glide / quadrupole
    output_ext = convert_ts_to_rgq(pmt, sig, cor_mat, l_max, fit_type)
    # fixed typo (ouput -> output)
    output = add_rgq_to_output(output, output_ext, l_max)

    # 5.3 bootstrap (optional; slow)
    if kwargs.get("bs_err", False):
        output = bootstrap_resample_4_err(
            mask, dra, ddc, dra_err, ddc_err,
            ra_rad, dc_rad, ra_dc_cor,
            l_max, fit_type, num_iter, output
        )

    if quiet:
        f.close()
        sys.stdout = old_target

    return output


def vsh_fit_4_table(
    data_tab,
    l_max: int = 1,
    fit_type: str = "full",
    pos_in_rad: bool = False,
    num_iter: int = 100,
    **kwargs,
):
    """
    VSH fit for an Astropy-like Table.

    Required columns:
      - 'ra', 'dec'
      - one of {'dra','pmra'}
      - one of {'ddec','pmdec'}
      - errors: prefer {'dra_err','ddec_err'}, fallbacks allowed (see code)
      - optional correlations: {'dra_ddec_cov','dra_ddec_cor','pmra_pmdec_corr','pmra_pmdec_cor'}
    """
    cols = data_tab.colnames

    if "dra" in cols:
        dra = np.array(data_tab["dra"])
    elif "pmra" in cols:
        dra = np.array(data_tab["pmra"])
    else:
        raise ValueError("'dra' or 'pmra' column is required.")

    if "ddec" in cols:
        ddec = np.array(data_tab["ddec"])
    elif "pmdec" in cols:
        ddec = np.array(data_tab["pmdec"])
    else:
        raise ValueError("'ddec' or 'pmdec' column is required.")

    ra = np.array(data_tab["ra"])
    dec = np.array(data_tab["dec"])

    if "dra_err" in cols:
        dra_err = np.array(data_tab["dra_err"])
    elif "dra_error" in cols:
        dra_err = np.array(data_tab["dra_error"])
    elif "pmra_err" in cols:
        dra_err = np.array(data_tab["pmra_err"])
    elif "pmra_error" in cols:
        dra_err = np.array(data_tab["pmra_error"])
    else:
        print("No RA error column found; using equal weights.")
        dra_err = np.ones(len(data_tab))

    if "ddec_err" in cols:
        ddec_err = np.array(data_tab["ddec_err"])
    elif "ddec_error" in cols:
        ddec_err = np.array(data_tab["ddec_error"])
    elif "pmdec_err" in cols:
        ddec_err = np.array(data_tab["pmdec_err"])
    elif "pmdec_error" in cols:
        ddec_err = np.array(data_tab["pmdec_error"])
    else:
        print("No Dec error column found; using equal weights.")
        ddec_err = np.ones(len(data_tab))

    if "dra_ddec_cov" in cols:
        dra_ddc_cov = np.array(data_tab["dra_ddec_cov"])
        dra_ddc_cor = dra_ddc_cov / (dra_err * ddec_err)
    elif "dra_ddec_cor" in cols:
        dra_ddc_cor = np.array(data_tab["dra_ddec_cor"])
    elif "pmra_pmdec_corr" in cols:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_corr"])
    elif "pmra_pmdec_cor" in cols:
        dra_ddc_cor = np.array(data_tab["pmra_pmdec_cor"])
    else:
        print("No RA/Dec correlation column found; assuming zero correlation.")
        dra_ddc_cor = None

    return vsh_fit(
        dra, ddec, dra_err, ddec_err, ra, dec,
        ra_dc_cor=dra_ddc_cor, l_max=l_max, pos_in_rad=pos_in_rad,
        num_iter=num_iter, fit_type=fit_type, **kwargs
    )


def rotgli_fit(
    dra,
    ddc,
    dra_err,
    ddc_err,
    ra,
    dc,
    ra_dc_cor=None,
    fit_type: str = "full",
    pos_in_rad: bool = False,
    num_iter: int = 100,
    **kwargs,
):
    """Degree-1 convenience wrapper returning the full `vsh_fit` dict."""
    return vsh_fit(
        dra, ddc, dra_err, ddc_err, ra, dc,
        ra_dc_cor=ra_dc_cor, l_max=1,
        fit_type=fit_type, pos_in_rad=pos_in_rad,
        num_iter=num_iter, **kwargs
    )


def rotgliquad_fit(
    dra,
    ddc,
    dra_err,
    ddc_err,
    ra,
    dc,
    ra_dc_cor=None,
    fit_type: str = "full",
    pos_in_rad: bool = False,
    num_iter: int = 100,
    **kwargs,
):
    """Degree-2 convenience wrapper returning the full `vsh_fit` dict."""
    return vsh_fit(
        dra, ddc, dra_err, ddc_err, ra, dc,
        ra_dc_cor=ra_dc_cor, l_max=2,
        fit_type=fit_type, pos_in_rad=pos_in_rad,
        num_iter=num_iter, **kwargs
    )


def rotgli_fit_4_table(data_tab, fit_type="full", pos_in_rad=False, num_iter=100, **kwargs):
    """Degree-1 fit for an Astropy-like Table."""
    return vsh_fit_4_table(
        data_tab, l_max=1, fit_type=fit_type, pos_in_rad=pos_in_rad, num_iter=num_iter, **kwargs
    )


def rotgliquad_fit_4_table(data_tab, fit_type="full", pos_in_rad=False, num_iter=100, **kwargs):
    """Degree-2 fit for an Astropy-like Table."""
    return vsh_fit_4_table(
        data_tab, l_max=2, fit_type=fit_type, pos_in_rad=pos_in_rad, num_iter=num_iter, **kwargs
    )


def main():
    pass


if __name__ == "__main__":
    main()
