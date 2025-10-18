#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name: tune_para.py
"""
Created on Tue Nov 24 13:13:45 2020

@author: Neo(niu.liu@nju.edu.cn)
"""

# -----------------------------  MAIN -----------------------------

from astropy.table import Table
import numpy as np
import time

# My modules
from vsh_tools.fit import vsh_fit
from vsh_tools.rgq import vsh_func
from pmt_convert import st_to_rotgldquad

# -----------------------------  MAIN -----------------------------


def generate_test_sample(sample_size, pmt_vec):
    """
    """

    # A sample of sources located as (ra, dec)
    ra = np.random.random_sample(sample_size) * 2 * np.pi
    dec = (np.random.random_sample(sample_size) - 0.5) * np.pi

    # Positional difference from ideal cases
    dra_calc, ddec_calc = vsh_func(ra, dec, pmt_vec, l_max=1)

    # Noise
    dra_nois = 0  # np.random.normal(scale=1, size=sample_size) * 0
    ddec_nois = 0  # np.random.normal(scale=1, size=sample_size) * 0

    # Simulation data
    dra_sim, ddec_sim = dra_calc + dra_nois, ddec_calc + ddec_nois

    # Formal error, uniform one
    dra_err = np.ones(sample_size)
    ddec_err = np.ones(sample_size)
    dra_ddec_cor = np.zeros(sample_size)

    # Generate a Astropy.Table and store the data
    data = Table([ra, dec, dra_sim, ddec_sim, dra_err, ddec_err, dra_ddec_cor],
                 names=["ra", "dec", "dra", "ddec", "dra_err", "ddec_err", "dra_ddec_cor"])

    return data


# Read the simulated data
rot_vec = np.array([20, 30, 15])
gli_vec = np.array([30, 24, 12])
qua_vec = np.array([-10, 20, -3, 5, 30, 9, 12, 39, 40, 12])
pmt_vec = np.concatenate((gli_vec, rot_vec, qua_vec))
test_tab = generate_test_sample(int(2e6), pmt_vec)

# Transform astropy.Column into np.array and mas -> dex
dra = np.array(test_tab["dra"])
ddec = np.array(test_tab["ddec"])
ra = np.array(test_tab["ra"])
dec = np.array(test_tab["dec"])
dra_err = np.array(test_tab["dra_err"])
ddec_err = np.array(test_tab["ddec_err"])
dra_ddc_cor = np.array(test_tab["dra_ddec_cor"])

print("# num_iter"
      "               Glide [dex]             "
      "               Rotation [dex]    Time_taken [s]")
print("#        "
      "     G1            G2            G3        "
      "     R1            R2            R3        ")
print("#        "
      "-----------------------------------------   "
      "-----------------------------------------")

print("#Input "
      "{0:4.0f}        0 {1:4.0f}        0 "
      "{2:4.0f}        0 {3:4.0f}        0 "
      "{4:4.0f}        0 {5:4.0f}        0 ".format(*pmt_vec[:6]))

for num_iter in np.arange(10, 201, 10):
    # Record the start time
    time_s = time.time()

    # DO the LSQ fitting
    pmt, err, cor_mat = vsh_fit(
        dra, ddec, dra_err, ddec_err, ra, dec, ra_dc_cor=dra_ddc_cor,
        l_max=2, pos_in_rad=True, num_iter=num_iter)

    # Record the end time
    time_d = time.time()
    # Time difference
    time_delta = time_d - time_s

    pmt1, err1, cor_mat1 = st_to_rotgldquad(pmt, err, cor_mat)

    print("{13:3.0f}  "
          "{0:4.0f}     {6:4.0f} {1:4.0f}     {7:4.0f} "
          "{2:4.0f}     {8:4.0f} {3:4.0f}     {9:4.0f} "
          "{4:4.0f}     {10:4.0f} {5:4.0f}     {11:4.0f}  "
          "{12:.0f}".format(*pmt1[:6], *err1[:6], time_delta, num_iter))


# --------------------------------- END --------------------------------
