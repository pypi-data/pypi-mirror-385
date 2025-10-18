#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: rgq.py
"""
VSH degree-1 (rotation + glide) and degree-2 (quadrupole) forward model.

Functions:
- vsh_func01: degree-1 field (R,G)
- vsh_func02: degree-2 field (E,M)
- vsh_func  : convenience wrapper for l_max in {1,2}
"""

from __future__ import annotations

import numpy as np
from numpy import sin, cos


__all__ = ["vsh_func01", "vsh_func02", "vsh_func"]


def _as_arrays(ra, dec):
    """Broadcast ra, dec to a common ndarray shape (radians)."""
    ra = np.asarray(ra, dtype=float)
    dec = np.asarray(dec, dtype=float)
    ra, dec = np.broadcast_arrays(ra, dec)
    return ra, dec


def vsh_func01(ra, dec, g1, g2, g3, r1, r2, r3):
    """
    Degree-1 VSH field (glide + rotation).

    Parameters
    ----------
    ra, dec : array_like
        Right ascension and declination in radians (broadcastable to same shape).
    g1,g2,g3 : float
        Glide components.
    r1,r2,r3 : float
        Rotation components.

    Returns
    -------
    dra, ddec : ndarray
        Tangential field components (Δα⋅cosδ, Δδ), same shape as broadcast(ra,dec).
    """
    ra, dec = _as_arrays(ra, dec)

    dra = (
        -r1 * cos(ra) * sin(dec)
        - r2 * sin(ra) * sin(dec)
        + r3 * cos(dec)
        - g1 * sin(ra)
        + g2 * cos(ra)
    )
    ddec = (
        + r1 * sin(ra)
        - r2 * cos(ra)
        - g1 * cos(ra) * sin(dec)
        - g2 * sin(ra) * sin(dec)
        + g3 * cos(dec)
    )
    return dra, ddec


def vsh_func02(
    ra,
    dec,
    ER_22,
    EI_22,
    ER_21,
    EI_21,
    E_20,
    MR_22,
    MI_22,
    MR_21,
    MI_21,
    M_20,
):
    """
    Degree-2 VSH field (electric E and magnetic M).

    Parameters
    ----------
    ra, dec : array_like
        Right ascension and declination in radians (broadcastable to same shape).
    ER_22, EI_22, ER_21, EI_21, E_20 : float
        Electric-type quadrupole parameters.
    MR_22, MI_22, MR_21, MI_21, M_20 : float
        Magnetic-type quadrupole parameters.

    Returns
    -------
    dra, ddec : ndarray
        Tangential field components (Δα⋅cosδ, Δδ) for the l=2 terms only.
    """
    ra, dec = _as_arrays(ra, dec)

    # Helpful shorthands
    s2ra, c2ra = sin(2 * ra), cos(2 * ra)
    sra, cra = sin(ra), cos(ra)
    s2d, c2d = sin(2 * dec), cos(2 * dec)
    sd, cd = sin(dec), cos(dec)

    dra = (
        + M_20 * s2d
        - (MR_21 * cra - MI_21 * sra) * c2d
        + (ER_21 * sra + EI_21 * cra) * sd
        # sin(2*dec)=2sd*cd; kept below for clarity
        - (MR_22 * c2ra - MI_22 * s2ra) * (2 * sd * cd)
        - 2.0 * (ER_22 * s2ra + EI_22 * c2ra) * cd
    )
    # Replace the previous line’s expansion for readability:
    dra = (
        + M_20 * s2d
        - (MR_21 * cra - MI_21 * sra) * c2d
        + (ER_21 * sra + EI_21 * cra) * sd
        - (MR_22 * c2ra - MI_22 * s2ra) * sin(2 * dec)
        - 2.0 * (ER_22 * s2ra + EI_22 * c2ra) * cd
    )

    ddec = (
        + E_20 * s2d
        - (MR_21 * sra + MI_21 * cra) * sd
        - (ER_21 * cra - EI_21 * sra) * c2d
        + 2.0 * (MR_22 * s2ra + MI_22 * c2ra) * cd
        - (ER_22 * c2ra - EI_22 * s2ra) *
        sin(2 * ra * 0 + 2 * dec)  # keep same as paper form
    )
    # Clean final ddec (the previous line keeps structure; simplify):
    ddec = (
        + E_20 * s2d
        - (MR_21 * sra + MI_21 * cra) * sd
        - (ER_21 * cra - EI_21 * sra) * c2d
        + 2.0 * (MR_22 * s2ra + MI_22 * c2ra) * cd
        - (ER_22 * c2ra - EI_22 * s2ra) * sin(2 * dec)
    )

    return dra, ddec


def vsh_func(ra, dec, pmt, l_max: int = 2):
    """
    Degree-1/2 VSH field wrapper.

    Parameters
    ----------
    ra, dec : array_like
        Right ascension and declination in radians (broadcastable).
    pmt : array_like
        Parameters. For l_max==1: length 6 -> (g1,g2,g3,r1,r2,r3)
                    For l_max==2: length 16 -> first 6 as above,
                                      then (ER_22, EI_22, ER_21, EI_21, E_20,
                                            MR_22, MI_22, MR_21, MI_21, M_20)
        (Order matches your existing code.)
    l_max : {1,2}
        Maximum degree to include.

    Returns
    -------
    dra, ddec : ndarray
        Tangential field components (Δα⋅cosδ, Δδ).
    """
    pmt = np.asarray(pmt, dtype=float)

    if l_max == 1:
        if pmt.size != 6:
            raise ValueError(
                "For l_max=1, pmt must have 6 elements (g1,g2,g3,r1,r2,r3).")
        return vsh_func01(ra, dec, *pmt)

    if l_max == 2:
        if pmt.size != 16:
            raise ValueError(
                "For l_max=2, pmt must have 16 elements: "
                "(g1,g2,g3,r1,r2,r3, ER_22,EI_22,ER_21,EI_21,E_20, MR_22,MI_22,MR_21,MI_21,M_20)."
            )
        dra1, ddec1 = vsh_func01(ra, dec, *pmt[:6])
        dra2, ddec2 = vsh_func02(ra, dec, *pmt[6:])
        return dra1 + dra2, ddec1 + ddec2

    raise ValueError("l_max must be 1 or 2.")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: rgq.py
"""
VSH degree-1 (rotation + glide) and degree-2 (quadrupole) forward model.

Functions:
- vsh_func01: degree-1 field (R,G)
- vsh_func02: degree-2 field (E,M)
- vsh_func  : convenience wrapper for l_max in {1,2}
"""


__all__ = ["vsh_func01", "vsh_func02", "vsh_func"]


def _as_arrays(ra, dec):
    """Broadcast ra, dec to a common ndarray shape (radians)."""
    ra = np.asarray(ra, dtype=float)
    dec = np.asarray(dec, dtype=float)
    ra, dec = np.broadcast_arrays(ra, dec)
    return ra, dec


def vsh_func01(ra, dec, g1, g2, g3, r1, r2, r3):
    """
    Degree-1 VSH field (glide + rotation).

    Parameters
    ----------
    ra, dec : array_like
        Right ascension and declination in radians (broadcastable to same shape).
    g1,g2,g3 : float
        Glide components.
    r1,r2,r3 : float
        Rotation components.

    Returns
    -------
    dra, ddec : ndarray
        Tangential field components (Δα⋅cosδ, Δδ), same shape as broadcast(ra,dec).
    """
    ra, dec = _as_arrays(ra, dec)

    dra = (
        -r1 * cos(ra) * sin(dec)
        - r2 * sin(ra) * sin(dec)
        + r3 * cos(dec)
        - g1 * sin(ra)
        + g2 * cos(ra)
    )
    ddec = (
        + r1 * sin(ra)
        - r2 * cos(ra)
        - g1 * cos(ra) * sin(dec)
        - g2 * sin(ra) * sin(dec)
        + g3 * cos(dec)
    )
    return dra, ddec


def vsh_func02(
    ra,
    dec,
    ER_22,
    EI_22,
    ER_21,
    EI_21,
    E_20,
    MR_22,
    MI_22,
    MR_21,
    MI_21,
    M_20,
):
    """
    Degree-2 VSH field (electric E and magnetic M).

    Parameters
    ----------
    ra, dec : array_like
        Right ascension and declination in radians (broadcastable to same shape).
    ER_22, EI_22, ER_21, EI_21, E_20 : float
        Electric-type quadrupole parameters.
    MR_22, MI_22, MR_21, MI_21, M_20 : float
        Magnetic-type quadrupole parameters.

    Returns
    -------
    dra, ddec : ndarray
        Tangential field components (Δα⋅cosδ, Δδ) for the l=2 terms only.
    """
    ra, dec = _as_arrays(ra, dec)

    # Helpful shorthands
    s2ra, c2ra = sin(2 * ra), cos(2 * ra)
    sra, cra = sin(ra), cos(ra)
    s2d, c2d = sin(2 * dec), cos(2 * dec)
    sd, cd = sin(dec), cos(dec)

    dra = (
        + M_20 * s2d
        - (MR_21 * cra - MI_21 * sra) * c2d
        + (ER_21 * sra + EI_21 * cra) * sd
        # sin(2*dec)=2sd*cd; kept below for clarity
        - (MR_22 * c2ra - MI_22 * s2ra) * (2 * sd * cd)
        - 2.0 * (ER_22 * s2ra + EI_22 * c2ra) * cd
    )
    # Replace the previous line’s expansion for readability:
    dra = (
        + M_20 * s2d
        - (MR_21 * cra - MI_21 * sra) * c2d
        + (ER_21 * sra + EI_21 * cra) * sd
        - (MR_22 * c2ra - MI_22 * s2ra) * sin(2 * dec)
        - 2.0 * (ER_22 * s2ra + EI_22 * c2ra) * cd
    )

    ddec = (
        + E_20 * s2d
        - (MR_21 * sra + MI_21 * cra) * sd
        - (ER_21 * cra - EI_21 * sra) * c2d
        + 2.0 * (MR_22 * s2ra + MI_22 * c2ra) * cd
        - (ER_22 * c2ra - EI_22 * s2ra) *
        sin(2 * ra * 0 + 2 * dec)  # keep same as paper form
    )
    # Clean final ddec (the previous line keeps structure; simplify):
    ddec = (
        + E_20 * s2d
        - (MR_21 * sra + MI_21 * cra) * sd
        - (ER_21 * cra - EI_21 * sra) * c2d
        + 2.0 * (MR_22 * s2ra + MI_22 * c2ra) * cd
        - (ER_22 * c2ra - EI_22 * s2ra) * sin(2 * dec)
    )

    return dra, ddec


def vsh_func(ra, dec, pmt, l_max: int = 2):
    """
    Degree-1/2 VSH field wrapper.

    Parameters
    ----------
    ra, dec : array_like
        Right ascension and declination in radians (broadcastable).
    pmt : array_like
        Parameters. For l_max==1: length 6 -> (g1,g2,g3,r1,r2,r3)
                    For l_max==2: length 16 -> first 6 as above,
                                      then (ER_22, EI_22, ER_21, EI_21, E_20,
                                            MR_22, MI_22, MR_21, MI_21, M_20)
        (Order matches your existing code.)
    l_max : {1,2}
        Maximum degree to include.

    Returns
    -------
    dra, ddec : ndarray
        Tangential field components (Δα⋅cosδ, Δδ).
    """
    pmt = np.asarray(pmt, dtype=float)

    if l_max == 1:
        if pmt.size != 6:
            raise ValueError(
                "For l_max=1, pmt must have 6 elements (g1,g2,g3,r1,r2,r3).")
        return vsh_func01(ra, dec, *pmt)

    if l_max == 2:
        if pmt.size != 16:
            raise ValueError(
                "For l_max=2, pmt must have 16 elements: "
                "(g1,g2,g3,r1,r2,r3, ER_22,EI_22,ER_21,EI_21,E_20, MR_22,MI_22,MR_21,MI_21,M_20)."
            )
        dra1, ddec1 = vsh_func01(ra, dec, *pmt[:6])
        dra2, ddec2 = vsh_func02(ra, dec, *pmt[6:])
        return dra1 + dra2, ddec1 + ddec2

    raise ValueError("l_max must be 1 or 2.")
