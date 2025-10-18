#!/usr/bin/env ipython
# -*- coding: utf-8 -*-
# File name: test_smoke_deg1.py
"""
Created on Sat 18 Oct 2025 03:41:25 PM CST

@author: Neo(niu.liu@nju.edu.cn)
"""


import numpy as np
from vsh_tools.generate_test_data import generate_test_sample
from vsh_tools.vsh_fit import vsh_fit
from vsh_tools.pmt_convert import st_to_rotgld


def test_deg1_smoke():
    # true params (g1,g2,g3,r1,r2,r3)
    rot = np.array([20., 30., 15.])
    gli = np.array([30., 24., 12.])
    p_true = np.r_[gli, rot]

    # small sample for speed
    tab = generate_test_sample(10000, p_true)  # returns ra/dec (rad)

    dra = np.array(tab["dra"])
    ddc = np.array(tab["ddec"])
    ra = np.array(tab["ra"])
    dec = np.array(tab["dec"])
    era = np.array(tab["dra_err"])
    edc = np.array(tab["ddec_err"])
    rho = np.array(tab["dra_ddec_cor"])

    out = vsh_fit(dra, ddc, era, edc, ra, dec,
                  ra_dc_cor=rho, l_max=1, fit_type="full",
                  pos_in_rad=True, num_iter=50, verbose=False)

    pmt = out["pmt"]
    sig = out["sig"]
    cor = out["cor"]
    gr, gr_err, _ = st_to_rotgld(pmt[:6], sig[:6], cor[:6], fit_type="full")

    # recovered glide & rotation should be close to truth (noise-free generator)
    est_gli = gr[:3]
    est_rot = gr[3:6]
    assert np.allclose(est_gli, gli, atol=1e-2)
    assert np.allclose(est_rot, rot, atol=1e-2)
