#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: transforms.py
"""
Convert real-basis S/T coefficients to rotation, glide, and quadrupolar parameters,
plus handy utilities like vector apex (amplitude + RA/Dec).
"""

from __future__ import annotations

import functools
import numpy as np

# from linalg helpers
from .linalg import cor_to_cov, cov_to_cor

__all__ = [
    "st_to_rotgld",
    "st_to_rotgldquad",
    "calc_vec_apex",
    "convert_ts_to_rgq",
    "add_rgq_to_output",
]

# Scaling factors between S/T and rotation/glide/quadrupolar parameters
FAC1 = np.sqrt(3.0 / (4.0 * np.pi))
FAC2 = np.sqrt(3.0 / (8.0 * np.pi))
FAC3 = np.sqrt(15.0 / (32.0 * np.pi))
FAC4 = np.sqrt(5.0 / (4.0 * np.pi))
FAC5 = np.sqrt(5.0 / (16.0 * np.pi))


# ----------------------------- degree 1: S/T -> (G,R) -----------------------------
def st_to_rotgld(pmt, err, cor_mat, fit_type: str = "full"):
    """
    Degree-1 transform from real-basis S/T to Glide/Rotation.

    Input packing (real basis):
        FULL: [T10, S10, T11r, S11r, T11i, S11i]  (len=6)
        T or S only: corresponding 3 terms           (len=3)

    Output order:
        [G1, G2, G3, R1, R2, R3]   for FULL
        [g1,g2,g3] or [r1,r2,r3]   for single-component fits
    """
    f = fit_type.lower()
    if f == "full":
        len_vec = 6
    elif f in {"t", "s"}:
        len_vec = 3
    else:
        raise ValueError(
            "fit_type must be one of {'full','T','S'} (case-insensitive).")

    pmt = np.asarray(pmt, dtype=float)
    err = np.asarray(err, dtype=float)
    cor_mat = np.asarray(cor_mat, dtype=float)
    if pmt.size != len_vec or err.size != len_vec or cor_mat.shape != (len_vec, len_vec):
        raise ValueError(
            f"Inputs must match length/shape {len_vec} (got pmt={pmt.size}, err={err.size}, cor_mat={cor_mat.shape}).")

    # Mapping:
    #   R1 = -FAC1 * T11r , R2 =  FAC1 * T11i , R3 = FAC2 * T10
    #   G1 = -FAC1 * S11r , G2 =  FAC1 * S11i , G3 = FAC2 * S10
    if f == "full":
        TSF_MAT = np.array([
            [0, 0, 0, -FAC1, 0,     0],  # G1 <- S11r
            [0, 0, 0, 0,     0,     FAC1],  # G2 <- S11i
            [0, FAC2, 0, 0,  0,     0],  # G3 <- S10
            [0, 0, -FAC1, 0,  0,     0],  # R1 <- T11r
            [0, 0, 0,     0,  FAC1,  0],  # R2 <- T11i
            [FAC2, 0, 0,   0,  0,     0],  # R3 <- T10
        ])
    else:
        # single component (T or S) mapped to 3-vector (R or G)
        TSF_MAT = np.array([
            [0, -FAC1, 0],
            [0, 0,  FAC1],
            [FAC2, 0, 0],
        ])

    gr_vec = TSF_MAT @ pmt

    cov_mat = cor_to_cov(err, cor_mat)
    gr_cov = functools.reduce(np.dot, [TSF_MAT, cov_mat, TSF_MAT.T])
    gr_err, gr_cor = cov_to_cor(gr_cov)

    return gr_vec, gr_err, gr_cor


# ----------------------------- degree 2: S/T -> (E,M) -----------------------------
def st_to_rotgldquad(pmt, err, cor_mat, fit_type: str = "full"):
    """
    Degree-1+2 transform from real-basis S/T -> (G,R,E,M) in a single vector.

    FULL packing (len=16):
        [T10,S10,T11r,S11r,T11i,S11i, T20,S20, T21r,S21r,T21i,S21i, T22r,S22r,T22i,S22i]
    T or S only (len=8) keeps the component (T or S) in the same order.
    """
    f = fit_type.lower()
    if f == "full":
        len_vec = 16
    elif f in {"t", "s"}:
        len_vec = 8
    else:
        raise ValueError(
            "fit_type must be one of {'full','T','S'} (case-insensitive).")

    pmt = np.asarray(pmt, dtype=float)
    err = np.asarray(err, dtype=float)
    cor_mat = np.asarray(cor_mat, dtype=float)
    if pmt.size != len_vec or err.size != len_vec or cor_mat.shape != (len_vec, len_vec):
        raise ValueError(
            f"Inputs must match length/shape {len_vec} (got pmt={pmt.size}, err={err.size}, cor_mat={cor_mat.shape}).")

    # Degree 1 mapping (top-left 6x6) identical to st_to_rotgld for FULL.
    # Degree 2 mapping:
    #   M20 = FAC3*T20 ; M21R = FAC4*T21r ; M21I = FAC4*T21i ; M22R = FAC5*T22r ; M22I = FAC5*T22i
    #   E20 = FAC3*S20 ; E21R = FAC4*S21r ; E21I = FAC4*S21i ; E22R = FAC5*S22r ; E22I = FAC5*S22i
    if f == "full":
        TSF_MAT = np.array([
            [0, 0, 0, -FAC1, 0,     0,     0, 0, 0,    0,
                0,    0,   0,    0,   0,    0],  # G1
            [0, 0, 0, 0,     0,     FAC1,  0, 0, 0,    0,
                0,    0,   0,    0,   0,    0],  # G2
            [0, FAC2, 0, 0,  0,     0,     0, 0, 0,    0,
                0,    0,   0,    0,   0,    0],  # G3
            [0, 0, -FAC1, 0, 0,     0,     0, 0, 0,    0,
                0,    0,   0,    0,   0,    0],  # R1
            [0, 0, 0,     0, FAC1,  0,     0, 0, 0,    0,
                0,    0,   0,    0,   0,    0],  # R2
            [FAC2, 0, 0,   0, 0,     0,     0, 0, 0,    0,
                0,    0,   0,    0,   0,    0],  # R3
            [0, 0, 0,     0, 0,     0,     0, 0, 0,    0,
                0,    0,   0,  FAC5, 0,    0],  # E22R
            [0, 0, 0,     0, 0,     0,     0, 0, 0,    0,
                0,    0,   0,    0,   0,  FAC5],  # E22I
            [0, 0, 0,     0, 0,     0,     0, 0, 0,  FAC4,
                0,    0,   0,    0,   0,    0],  # E21R
            [0, 0, 0,     0, 0,     0,     0, 0, 0,    0,
                0,  FAC4, 0,    0,   0,    0],  # E21I
            [0, 0, 0,     0, 0,     0,     0, FAC3, 0, 0,
                0,    0,   0,    0,   0,    0],  # E20
            [0, 0, 0,     0, 0,     0,     0, 0, 0,    0,
                0,    0, FAC5,  0,   0,    0],  # M22R
            [0, 0, 0,     0, 0,     0,     0, 0, 0,    0,
                0,    0,   0,    0, FAC5,  0],  # M22I
            [0, 0, 0,     0, 0,     0,     0, 0, FAC4, 0,
                0,    0,   0,    0,   0,    0],  # M21R
            [0, 0, 0,     0, 0,     0,     0, 0, 0,    0,
                FAC4,  0,   0,    0,   0,    0],  # M21I
            [0, 0, 0,     0, 0,     0,   FAC3, 0, 0,   0,
                0,    0,   0,    0,   0,    0],  # M20
        ])
    else:
        # Single component (T or S) degree-1+2 -> 8 targets
        TSF_MAT = np.array([
            [0, -FAC1, 0, 0, 0, 0, 0, 0],  # g1/r1
            [0, 0,  FAC1, 0, 0, 0, 0, 0],  # g2/r2
            [FAC2, 0, 0, 0, 0, 0, 0, 0],   # g3/r3
            [0, 0, 0, 0, 0, FAC5, 0, 0],   # 22R
            [0, 0, 0, 0, 0, 0, FAC5, 0],   # 22I
            [0, 0, 0, FAC4, 0, 0, 0, 0],   # 21R
            [0, 0, 0, 0, FAC4, 0, 0, 0],   # 21I
            [0, 0, 0, 0, 0, 0, 0, FAC3],   # 20
        ])

    grq_vec = TSF_MAT @ pmt
    cov_mat = cor_to_cov(err, cor_mat)
    grq_cov = functools.reduce(np.dot, [TSF_MAT, cov_mat, TSF_MAT.T])
    grq_err, grq_cor = cov_to_cor(grq_cov)
    return grq_vec, grq_err, grq_cor


# ----------------------------- vector apex -----------------------------
def calc_vec_apex(pmt, err, cor_mat):
    """
    Apex (amplitude + RA/Dec) and uncertainties for a 3D vector.

    Returns
    -------
    new_pmt : [amp, RA_deg, Dec_deg]
    new_err : [σ_amp, σ_RA_deg, σ_Dec_deg]
    """
    pmt = np.asarray(pmt, dtype=float).reshape(3)
    err = np.asarray(err, dtype=float).reshape(3)
    cor_mat = np.asarray(cor_mat, dtype=float).reshape(3, 3)

    g = float(np.sqrt(np.sum(pmt ** 2)))
    if g == 0.0:
        # degenerate: zero vector; uncertainties still computed from linearization
        g = 1e-20

    RA_rad = float(np.arctan2(pmt[1], pmt[0]))
    if RA_rad < 0:
        RA_rad += 2.0 * np.pi
    DC_rad = float(np.arctan2(pmt[2], np.sqrt(pmt[0] ** 2 + pmt[1] ** 2)))

    RA_deg = float(np.rad2deg(RA_rad))
    DC_deg = float(np.rad2deg(DC_rad))

    cov = cor_to_cov(err, cor_mat)

    # Jacobian ∂(g, RA, Dec)/∂(g1,g2,g3)
    par_g = pmt / g
    gxy2 = pmt[0] ** 2 + pmt[1] ** 2
    gxy = np.sqrt(max(gxy2, 1e-20))

    par_RA = np.array([-pmt[1], pmt[0], 0.0]) / max(gxy2, 1e-20)
    par_DC = np.array([-pmt[0] * pmt[2], -pmt[1] *
                      pmt[2], gxy2]) / (g**2 * gxy)

    J = np.vstack((par_g, par_RA, par_DC))
    new_cov = functools.reduce(np.dot, [J, cov, J.T])

    new_err, _ = cov_to_cor(new_cov)
    g_err = float(new_err[0])
    RA_err = float(np.rad2deg(new_err[1]))
    DC_err = float(np.rad2deg(new_err[2]))

    return [g, RA_deg, DC_deg], [g_err, RA_err, DC_err]


# ----------------------------- helpers: user-facing conversions -----------------------------
def convert_ts_to_rgq(pmt, err, cor_mat, l_max: int, fit_type: str = "full"):
    """
    Convert packed real-basis S/T coefficients to:
      - degree-1 Glide/Rotation (always returned)
      - degree-2 Electric/Magnetic (if l_max>=2 and using st_to_rotgldquad)

    Returns dict with keys:
      pmt1, sig1, cor_mat1 (degree 1)
      (plus R/G apex entries; if l_max>=2 you can also keep the degree-2 part)
    """
    f = fit_type.lower()
    pmt = np.asarray(pmt, dtype=float)
    err = np.asarray(err, dtype=float)
    cor_mat = np.asarray(cor_mat, dtype=float)

    # choose slice lengths
    if l_max == 1:
        n_single = 3
        n_full = 6
    elif l_max >= 2:
        n_single = 8
        n_full = 16
    else:
        raise ValueError(f"Invalid l_max={l_max}.")

    if f == "full":
        n = n_full
    elif f in {"t", "s"}:
        n = n_single
    else:
        raise ValueError(
            "fit_type must be one of {'full','T','S'} (case-insensitive).")

    if pmt.size < n or err.size < n or cor_mat.shape[0] < n or cor_mat.shape[1] < n:
        raise ValueError(
            f"Input vectors/matrix too short for l_max={l_max}, fit_type='{fit_type}' (need {n}).")

    output = {}

    if l_max == 1:
        p1, e1, C1 = st_to_rotgld(pmt[:n], err[:n], cor_mat[:n, :n], fit_type)
    else:  # l_max >= 2
        p1, e1, C1 = st_to_rotgldquad(
            pmt[:n], err[:n], cor_mat[:n, :n], fit_type)

    # Build a 6-vector to print G/R nicely even for single-component fits
    if f == "t":
        pmt1_out = np.hstack(([0.0, 0.0, 0.0], p1))
        err1_out = np.hstack(([0.0, 0.0, 0.0], e1))
        r_vec, r_vec_err = calc_vec_apex(p1, e1, C1)
        g_vec, g_vec_err = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    elif f == "s":
        pmt1_out = np.hstack((p1, [0.0, 0.0, 0.0]))
        err1_out = np.hstack((e1, [0.0, 0.0, 0.0]))
        r_vec, r_vec_err = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
        g_vec, g_vec_err = calc_vec_apex(p1, e1, C1)
    else:  # full
        pmt1_out = p1
        err1_out = e1
        r_vec, r_vec_err = calc_vec_apex(p1[3:6], e1[3:6], C1[3:6, 3:6])
        g_vec, g_vec_err = calc_vec_apex(p1[0:3], e1[0:3], C1[0:3, 0:3])

    # Pretty print (degree 1)
    print("")
    print("Convert t_lm/s_lm at l=1 into rotation/glide vector")
    print("--------------------------------------------------------------------")
    print(
        "           Glide [dex]                     Rotation [dex]           ")
    print("    G1         G2         G3               R1         R2         R3 ")
    print("--------------------------------------------------------------------")
    print("{0:+8.3f} {6:8.3f}  {1:+8.3f} {7:8.3f}  {2:+8.3f} {8:8.3f}   {3:+8.3f} {9:8.3f}  {4:+8.3f} {10:8.3f}  {5:+8.3f} {11:8.3f}".format(
        *pmt1_out[:6], *err1_out[:6]
    ))
    print("--------------------------------------------------------------------")

    output["pmt1"] = p1
    output["sig1"] = e1
    output["cor_mat1"] = C1

    output["R"], output["R_err"] = r_vec[0], r_vec_err[0]
    output["R_ra"], output["R_ra_err"] = r_vec[1], r_vec_err[1]
    output["R_dec"], output["R_dec_err"] = r_vec[2], r_vec_err[2]

    output["G"], output["G_err"] = g_vec[0], g_vec_err[0]
    output["G_ra"], output["G_ra_err"] = g_vec[1], g_vec_err[1]
    output["G_dec"], output["G_dec_err"] = g_vec[2], g_vec_err[2]

    return output


def add_rgq_to_output(output, output_ext, l_max: int):
    """
    Merge degree-1 (and degree-2 if available) converted parameters into `output`.
    """
    if l_max == 1:
        output["pmt1"] = output_ext["pmt1"]
        output["sig1"] = output_ext["sig1"]
        output["cor1"] = output_ext["cor_mat1"]
        output["note"] = output.get("note", []) + [
            "pmt1: glide+rotation",
            "sig1: formal error of glide/rotation",
            "cor1: correlation coefficient matrix of glide/rotation",
        ]
    elif l_max >= 2:
        output["pmt2"] = output_ext["pmt1"]
        output["sig2"] = output_ext["sig1"]
        output["cor2"] = output_ext["cor_mat1"]  # fixed bug (was sig1)
        output["note"] = output.get("note", []) + [
            "pmt2: glide+rotation+quadrupolar",
            "sig2: formal error of glide/rotation/quadrupolar",
            "cor2: correlation coefficient matrix of glide/rotation/quad",
        ]
    else:
        raise ValueError(f"Invalid l_max={l_max}.")

    output["R"], output["R_err"] = output_ext["R"], output_ext["R_err"]
    output["R_ra"], output["R_ra_err"] = output_ext["R_ra"], output_ext["R_ra_err"]
    output["R_dec"], output["R_dec_err"] = output_ext["R_dec"], output_ext["R_dec_err"]

    output["G"], output["G_err"] = output_ext["G"], output_ext["G_err"]
    output["G_ra"], output["G_ra_err"] = output_ext["G_ra"], output_ext["G_ra_err"]
    output["G_dec"], output["G_dec_err"] = output_ext["G_dec"], output_ext["G_dec_err"]

    # keep notes as a list; callers can join/print as they like
    return output


def main():
    pass


if __name__ == "__main__":
    main()
