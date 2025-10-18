#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: test_smoke_deg2.py
"""
Created on Sat 18 Oct 2025 03:41:49 PM CST

@author: Neo(niu.liu@nju.edu.cn)
"""


import numpy as np
from vsh_tools.generate_test_data import generate_test_sample
from vsh_tools.vsh_fit import vsh_fit
from vsh_tools.pmt_convert import st_to_rotgldquad


def test_deg2_smoke():
    rot = np.array([20., 30., 15.])
    gli = np.array([30., 24., 12.])
    qua = np.array([-10., 20., -3., 5., 30., 9., 12., 39., 40., 12.])
    p_true = np.r_[gli, rot, qua]

    tab = generate_test_sample(15000, p_true, l_max=2)

    dra = np.array(tab["dra"])
    ddc = np.array(tab["ddec"])
    ra = np.array(tab["ra"])
    dec = np.array(tab["dec"])
    era = np.array(tab["dra_err"])
    edc = np.array(tab["ddec_err"])
    rho = np.array(tab["dra_ddec_cor"])

    out = vsh_fit(dra, ddc, era, edc, ra, dec,
                  ra_dc_cor=rho, l_max=2, fit_type="full",
                  pos_in_rad=True, num_iter=50, verbose=False)

    pmt = out["pmt"]
    sig = out["sig"]
    cor = out["cor"]
    grq, grq_err, _ = st_to_rotgldquad(
        pmt[:16], sig[:16], cor[:16, :16], fit_type="full")

    # check just dipole portion for tightness
    est_gli = grq[:3]
    est_rot = grq[3:6]
    assert np.allclose(est_gli, gli, atol=1e-2)
    assert np.allclose(est_rot, rot, atol=1e-2)
