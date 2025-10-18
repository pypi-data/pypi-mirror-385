#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: glide.py
"""
Glide utilities:
- build a glide vector from amplitude + apex
- recover amplitude + apex from a glide vector
- decompose into GA (Galactic-acceleration) and non-GA parts
- generate/plot the induced sky field
"""

from __future__ import annotations

import numpy as np
from numpy import sin, cos
import matplotlib.pyplot as plt

from astropy.coordinates import SkyCoord
from astropy import units as u

__all__ = [
    "glide_gen",
    "glide_apex_calc",
    "GA_glide_decomposed",
    "glide_field_gen",
    "glide_plot",
]


# -----------------------------  CORE -----------------------------
def glide_gen(g: float, RAdeg: float, DCdeg: float, err: np.ndarray | None = None):
    """
    Given amplitude and apex (RA, Dec in deg), return the glide vector [g1,g2,g3].
    If `err=[σ_g, σ_RA_deg, σ_Dec_deg]` is provided, also return propagated
    component uncertainties assuming independent errors.

    Notes
    -----
    - Does NOT mutate the input `err`.
    """
    RArad = np.deg2rad(RAdeg)
    DCrad = np.deg2rad(DCdeg)

    g1 = g * cos(RArad) * cos(DCrad)
    g2 = g * sin(RArad) * cos(DCrad)
    g3 = g * sin(DCrad)

    if err is None:
        return np.array([g1, g2, g3])

    err = np.asarray(err, dtype=float).copy()
    if err.size != 3:
        raise ValueError("err must be [σ_g, σ_RA_deg, σ_Dec_deg].")

    # Jacobian ∂(g1,g2,g3)/∂(g,RA,Dec) with RA/Dec in radians
    sigma_g, sigma_RA_deg, sigma_DC_deg = err
    sigma_RA = np.deg2rad(sigma_RA_deg)
    sigma_DC = np.deg2rad(sigma_DC_deg)

    J = np.array([
        [cos(RArad) * cos(DCrad),        -g * sin(RArad)
         * cos(DCrad),  -g * cos(RArad) * sin(DCrad)],
        [sin(RArad) * cos(DCrad),         g * cos(RArad)
         * cos(DCrad),  -g * sin(RArad) * sin(DCrad)],
        [sin(DCrad),                      0.0,
         g * cos(DCrad)],
    ])
    cov_input = np.diag([sigma_g**2, sigma_RA**2, sigma_DC**2])
    comp_var = np.einsum("ij,jk,ik->i", J, cov_input, J)
    errn = np.sqrt(comp_var)

    return np.array([g1, g2, g3]), errn


def glide_apex_calc(gv: np.ndarray, err_gv: np.ndarray | None = None):
    """
    From glide vector [g1,g2,g3], return amplitude and apex (deg).
    If `err_gv=[σ_g1,σ_g2,σ_g3]` is provided, propagate uncertainties.

    Returns
    -------
    If err_gv is None:
        g, RAdeg, DCdeg
    Else:
        g, RAdeg, DCdeg, σ_g, σ_RAdeg, σ_DCdeg
    """
    gv = np.asarray(gv, dtype=float).reshape(3)
    g = float(np.linalg.norm(gv))

    # Right ascension in [0, 2π)
    RArad = float(np.arctan2(gv[1], gv[0]))
    if RArad < 0:
        RArad += 2.0 * np.pi

    # Declination
    gxy2 = float(gv[0] ** 2 + gv[1] ** 2)
    DCrad = float(np.arctan2(gv[2], np.sqrt(gxy2)))

    RAdeg = float(np.rad2deg(RArad))
    DCdeg = float(np.rad2deg(DCrad))

    if err_gv is None:
        return g, RAdeg, DCdeg

    err_gv = np.asarray(err_gv, dtype=float).reshape(3)

    # Jacobian ∂(g,RA,Dec)/∂(g1,g2,g3) with numerically safe guards
    eps = 1e-20
    g_safe = g if g > eps else eps
    gxy2_safe = gxy2 if gxy2 > eps else eps
    gxy = np.sqrt(gxy2_safe)

    par_g = gv / g_safe
    par_RA = np.array([-gv[1], gv[0], 0.0]) / gxy2_safe
    par_DC = np.array([-gv[0] * gv[2], -gv[1] * gv[2],
                      gxy2_safe]) / (g_safe**2 * gxy)

    sigma_g = float(np.sqrt(np.sum((par_g * err_gv) ** 2)))
    sigma_RA = float(np.sqrt(np.sum((par_RA * err_gv) ** 2)))
    sigma_Dec = float(np.sqrt(np.sum((par_DC * err_gv) ** 2)))

    return g, RAdeg, DCdeg, sigma_g, float(np.rad2deg(sigma_RA)), float(np.rad2deg(sigma_Dec))


def GA_glide_decomposed(gv: np.ndarray, err_gv: np.ndarray | None):
    """
    Decompose a glide vector into GA (toward Galactic center) and non-GA parts.

    We take the GA direction (ICRS) ≈ (RA,Dec) = (266.4°, -28.9°).

    Returns
    -------
    [G_GA, σ_GA, G_nonGA, RA_nonGA, DC_nonGA, σ_G_nonGA, σ_RA_nonGA, σ_DC_nonGA]
    """
    gv = np.asarray(gv, dtype=float).reshape(3)
    GA_hat = glide_gen(1.0, 266.4, -28.9)  # unit direction

    # Projection amplitude onto GA direction
    G_GA = float(np.dot(gv, GA_hat))

    # Uncertainty of the projection (assuming independent component errors)
    if err_gv is None:
        sigma_GA = np.nan
        err_for_nonGA = None
    else:
        err_gv = np.asarray(err_gv, dtype=float).reshape(3)
        sigma_GA = float(np.sqrt(np.dot(GA_hat**2, err_gv**2)))
        err_for_nonGA = err_gv

    g_nonGA = gv - G_GA * GA_hat
    out = list(glide_apex_calc(g_nonGA, err_for_nonGA)
               ) if err_for_nonGA is not None else list(glide_apex_calc(g_nonGA))

    return [G_GA, sigma_GA, *out]


# -----------------------------  FIELD / PLOT -----------------------------
def glide_field_gen(gv: np.ndarray, ra: np.ndarray, dec: np.ndarray):
    """
    Induced field (Δα⋅cosδ, Δδ) at (ra,dec) in radians for glide vector gv=[g1,g2,g3].
    """
    g1, g2, g3 = gv
    g_dra = -g1 * sin(ra) + g2 * cos(ra)
    g_ddec = -g1 * cos(ra) * sin(dec) - g2 * sin(ra) * sin(dec) + g3 * cos(dec)
    return g_dra, g_ddec


def glide_plot(gv: np.ndarray, output: str | None = None, fig_title: str | None = None):
    """
    Aitoff quiver plot of the glide field. Units are arbitrary (vector lengths are scaled).
    """
    ra = np.linspace(0, 360, 20) * u.deg
    dec = np.linspace(-90, 90, 20) * u.deg
    c = SkyCoord(ra=ra, dec=dec, frame="icrs")

    ra_rad = c.ra.wrap_at(180 * u.deg).radian
    dec_rad = c.dec.radian

    X, Y = np.meshgrid(ra_rad, dec_rad)
    U, V = glide_field_gen(gv, X, Y)

    # Galactic center and anti-center in ICRS
    gc = SkyCoord(l=0 * u.deg, b=0 * u.deg, frame="galactic").icrs
    agc = SkyCoord(l=180 * u.deg, b=0 * u.deg, frame="galactic").icrs
    ra_gc, dec_gc = gc.ra.wrap_at(180 * u.deg).radian, gc.dec.radian
    ra_agc, dec_agc = agc.ra.wrap_at(180 * u.deg).radian, agc.dec.radian

    plt.figure(figsize=(8, 4.2))
    ax = plt.subplot(111, projection="aitoff")

    Q = ax.quiver(X, Y, U, V, units="xy", scale=100.0)
    ax.quiverkey(Q, 0.90, 0.90, 50,
                 r"$50 \,\mu\mathrm{as}$", labelpos="E", coordinates="figure")

    ax.plot(ra_gc, dec_gc, "r+")
    ax.plot(ra_agc, dec_agc, "r+")
    ax.text(ra_gc, dec_gc, "GC", color="r")

    if fig_title:
        ax.set_title(fig_title, y=1.08)

    ax.grid(True)
    plt.subplots_adjust(top=0.95, bottom=0.05)

    if output:
        plt.savefig(output, bbox_inches="tight", dpi=200)
        plt.close()
    else:
        plt.show()
