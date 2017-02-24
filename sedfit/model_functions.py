import numpy as np
import cPickle as pickle
from collections import OrderedDict
from models.model_bc03 import BC03_Template
from models.model_dl07 import DL07, DL07_PosPar
import models.model_analyticals as ma
from models.model_xl import Torus_Emission, Torus_Emission_PosPar
from models.model_clumpy import CLUMPY_intp
from models.model_pah import pah
if __name__ == "__main__":
    from sedfit.fitter.template import Template
    from sedfit.dir_list import template_path
else:
    from fitter.template import Template
    from dir_list import template_path
#CLUMPY_intp = None

#->Setup the analytical models
Linear = ma.Linear
BlackBody = ma.BlackBody
Modified_BlackBody = ma.Modified_BlackBody
Power_Law = ma.Power_Law
Synchrotron = ma.Synchrotron
Line_Gaussian_L = ma.Line_Gaussian_L

#->The stellar emission model using Bruzual & Charlot (2003) templates.
fp = open(template_path+"bc03_kdt.tmplt")
tp_bc03 = pickle.load(fp)
fp.close()
BC03 = BC03_Template(Template(**tp_bc03))


#Dict of the supporting functions
funcLib = {
    "Linear":{
        "function": Linear,
        "x_name": "x",
        "param_fit": ["a", "b"],
        "param_add": []
    },
    "BC03":{
        "function": BC03,
        "x_name": "wave",
        "param_fit": ["logMs", "age"],
        "param_add": ["DL", "z", "frame"],
    },
    "CLUMPY_intp": {
        "function": CLUMPY_intp,
        "x_name": "wave",
        "param_fit": ["logL", "i", "tv", "q", "N0", "sigma", "Y"],
        "param_add": ["DL", "z", "frame", "t"]
    },
    "Torus_Emission": {
        "function": Torus_Emission,
        "x_name": "wave",
        "param_fit": ["typeSil", "size", "T1Sil", "T2Sil", "logM1Sil", "logM2Sil",
                      "typeGra", "T1Gra", "T2Gra", "R1G2S", "R2G2S"],
        "param_add": ["DL", "z", "frame", "TemplateSil", "TemplateGra"]
    },
    "DL07": {
        "function": DL07,
        "x_name": "wave",
        "param_fit": ["logumin", "logumax", "qpah", "gamma", "logMd"],
        "param_add": ["t", "DL", "z", "frame"]
    },
    "BlackBody": {
        "function": BlackBody,
        "x_name": "wave",
        "param_fit": ["logOmega", "T"],
        "param_add": []
    },
    "Modified_BlackBody": {
        "function": Modified_BlackBody,
        "x_name": "wave",
        "param_fit": ["logM", "beta", "T"],
        "param_add": ["DL", "z", "kappa0", "lambda0", "frame"]
    },
    "Power_Law": {
        "function": Power_Law,
        "x_name": "wave",
        "param_fit": ["PL_alpha", "PL_logsf"],
        "param_add": []
    },
    "Synchrotron": {
        "function": Synchrotron,
        "x_name": "wave",
        "param_fit": ["Sn_alpha", "Sn_logsf"],
        "param_add": ["lognuc", "lognum"]
    },
    "Line_Gaussian_L": {
        "function": Line_Gaussian_L,
        "x_name": "wavelength",
        "param_fit": ["logLum", "lambda0", "FWHM"],
        "param_add": ["DL"]
    },
    "pah": {
        "function": pah,
        "x_name": "wave",
        "param_fit": ["logLpah"],
        "param_add": ["t", "DL", "z", "frame", "waveLim"]
    }
}

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    wave = 10**np.linspace(-1, 3, 1000)
    flux = BC03(9, 2.456, 50, wave, 0.001)
    print BC03.discretize_parameters(9, 2.456)
    plt.plot(wave, flux)
    plt.xscale("log")
    plt.yscale("log")
    plt.ylim([5e-4, 1e1])
    plt.show()

"""
ls_mic = 2.99792458e14 #unit: micron/s
m_H = 1.6726219e-24 #unit: gram
Msun = 1.9891e33 #unit: gram
Mpc = 3.08567758e24 #unit: cm
mJy = 1e26 #unit: erg/s/cm^2/Hz
"""
