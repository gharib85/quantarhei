# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from quantarhei.spectroscopy.twod2 import TwoDSpectrumContainer
from quantarhei import energy_units

rwa_cm = 12000
w1_min = rwa_cm - 700.0
w1_max = rwa_cm + 700.0
w3_min = rwa_cm - 700.0
w3_max = rwa_cm + 700.0

window_2D = [w1_min, w1_max, w3_min, w3_max]
off = 0
window_trim = [w1_min-off, w1_max+off, w3_min-off, w3_max+off]

newtw = TwoDSpectrumContainer()
newtw.load("allspectra.hdf5")

with energy_units("1/cm"):

    print("Making movie:\n")  
    newtw.make_movie("test_movie.mp4", 
                     cmap=plt.cm.jet, 
                     dpi=200,
                     Npos_contours=10,
                     stype="total",
                     spart="imaginary")

    