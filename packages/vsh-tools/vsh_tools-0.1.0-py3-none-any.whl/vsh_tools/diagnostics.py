#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: diagnostics.py
"""
Small pre-fit checks and info printing for VSH fits.
"""

from __future__ import annotations

__all__ = ["prefit_check", "prefit_info"]


def prefit_check(num_sou: int, num_pmt: int) -> None:
    """
    Validate that the system is solvable: 2*#sources >= #unknowns.

    Parameters
    ----------
    num_sou : int
        Number of sources (each contributes 2 observables: RA, Dec).
    num_pmt : int
        Number of unknown parameters to solve.

    Raises
    ------
    ValueError
        If the sample is insufficient.
    """
    if 2 * num_sou < num_pmt:
        raise ValueError(
            f"The sample of {num_sou} sources is insufficient for determining {num_pmt} unknowns."
        )


def prefit_info(num_sou: int, num_pmt: int, num_dof: int, l_max: int) -> None:
    """
    Print a compact pre-fit summary.
    """
    print("")
    print("Pre-fit information:")
    print(f"    Number of sources                {num_sou:10d}")
    print(f"    Maximum degree of VSH            {l_max:10d}")
    print(f"    Number of unknowns to determine  {num_pmt:10d}")
    print(f"    Number of degree of freedom      {num_dof:10d}")
    print("")
