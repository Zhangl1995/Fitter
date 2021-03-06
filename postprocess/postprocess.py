#!/Users/jinyi/anaconda/bin/python

from __future__ import print_function
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib_version = eval(matplotlib.__version__.split(".")[0])
if matplotlib_version > 1:
    plt.style.use("classic")
plt.rc('font',family='Times New Roman')
import sys
import types
import numpy as np
import cPickle as pickle
import sedfit.SED_Toolkit as sedt
from sedfit.mcmc import mcmc_emcee as mcmc
from PostProcessTools import *
from matplotlib.ticker import FuncFormatter, FormatStrFormatter

ls_mic = 2.99792458e14 #micron/s

xlabelDict = {
    "cm": r'$\lambda \, \mathrm{(cm)}$',
    "mm": r'$\lambda \, \mathrm{(mm)}$',
    "micron": r'$\lambda \, \mathrm{(\mu m)}$',
    "angstrom": r'$\lambda \, \mathrm{(\AA)}$',
    "Hz": r'$\nu \, \mathrm{(Hz)}$',
    "MHz": r'$\nu \, \mathrm{(MHz)}$',
    "GHz": r'$\nu \, \mathrm{(GHz)}$',
}
ylabelDict = {
    "fnu": r'$f_\nu \, \mathrm{(mJy)}$',
    "nufnu": r'$\nu f_\nu \, \mathrm{(erg\,s^{-1}\,cm^{-2})}$',
}

#Parse the commands#
#-------------------#
fitrsFile = sys.argv[1]
fp = open(fitrsFile, "r")
fitrs = pickle.load(fp)
fp.close()
#--> Dump the model dict
dumpModelDict(fitrs)

#The code starts#
#################
print("#################################")
print("# Galaxy SED Fitter postprocess #")
print("#################################")

silent = True
dataPck = fitrs["dataPck"]
targname = dataPck["targname"]
redshift = dataPck["redshift"]
distance = dataPck["distance"]
dataDict = dataPck["dataDict"]
modelPck = fitrs["modelPck"]
print("The target info:")
print("Name: {0}".format(targname))
print("Redshift: {0}".format(redshift))
print("Distance: {0}".format(distance))

#-> Load the data
sedData = dataLoader(fitrs, silent)

#-> Load the model
sedModel = modelLoader(fitrs, silent)
cleanTempFile()
parTruth = modelPck["parTruth"]   #Whether to provide the truth of the model
modelUnct = False #modelPck["modelUnct"] #Whether to consider the model uncertainty in the fitting

#-> Build the emcee object
em = mcmc.EmceeModel(sedData, sedModel, modelUnct)

#posterior process settings#
#--------------------------#
ppDict   = fitrs["ppDict"]
psLow    = ppDict["low"]
psCenter = ppDict["center"]
psHigh   = ppDict["high"]
nuisance = ppDict["nuisance"]
fraction = 0
burnIn = 0
ps = fitrs["posterior_sample"]

#-> Plot the SED data and fit
xUnits = "micron"
yUnits = "nufnu"
sedwave = np.array(sedData.get_List("x"))
sedflux = np.array(sedData.get_List("y"))
if yUnits == "nufnu":
    sedflux *= ls_mic / sedwave * 1.e-26
fig = plt.figure(figsize=(10, 5))
ax = plt.gca()
xmin = np.min(sedwave) * 0.9 #0.7 #
xmax = np.max(sedwave) * 1.1 #600 #
ymin = np.min(sedflux) * 0.5
ymax = np.max(sedflux) * 3.0
xlim = [xmin, xmax]
ylim = [ymin, ymax]
cList = ["green", "orange", "blue", "yellow", "purple"]
cKwargs = { #The line properties of the model components.
    "ls_uc": "--",
    "alpha_uc": 0.1,
    "lw_uc": 0.5,
    "ls_bf": "--",
    "alpha_bf": 1.0,
    "lw_bf": 1.0,
}
tKwargs = { #The line properties of the model total.
    "ls_uc": "-",
    "alpha_uc": 0.1,
    "lw_uc": 0.5,
    "ls_bf": "-",
    "alpha_bf": 1.0,
    "lw_bf": 3.0,
    "color": "red",
}
em.plot_fit(truths=parTruth, FigAx=(fig, ax), xlim=xlim, ylim=ylim, nSamples=100,
            burnin=burnIn, fraction=fraction, cList=cList, cLineKwargs=cKwargs,
            tLineKwargs=tKwargs, ps=ps, xUnits=xUnits, yUnits=yUnits)
#ax.set_xlabel(r"Rest Wavelength ($\mu$m)", fontsize=24)
#ax.set_ylabel(r"$f_\nu \, \mathrm{(mJy)}$", fontsize=24)
#plotName = r"{0}".format(targname)
#plotName = r"PG {0}${1}${2}".format(targname[2:6], targname[6], targname[7:])
#plotName = r"SDSS {0}${1}${2}".format(targname[4:9], targname[9], targname[10:])
#plotName = r"{0}${1}${2}".format(targname[0:5], targname[5], targname[6:])
plotName = targname
nameSeg  = plotName.split("-")
if (len(nameSeg) > 1):
    plotName = "$-$".join(nameSeg)
#plotName = "SDSS {0}".format(plotName[4:])
ax.text(0.05, 0.95, "{0}".format(plotName),
        verticalalignment='top', horizontalalignment='left',
        transform=ax.transAxes, fontsize=24,
        bbox=dict(facecolor='white', alpha=0.5, edgecolor="none"))
#"""
ax.text(0.95, 0.95, "d",
        verticalalignment='top', horizontalalignment='right',
        transform=ax.transAxes, fontsize=24,
        bbox=dict(facecolor='white', alpha=0.5, edgecolor="none"))
#"""
ax.tick_params(axis="both", which="major", length=8, labelsize=18, direction="in")
ax.tick_params(axis="both", which="minor", length=5)
#-->Set the legend
phtName = dataDict["phtName"]
spcName = dataDict["spcName"]
handles, labels = ax.get_legend_handles_labels()
handleUse = []
labelUse  = []
for loop in range(len(labels)):
    lb = labels[loop]
    hd = handles[loop]
    if lb == "Cat3d_H":
        lb = "CAT3D"
    #if lb == "Hot_Dust":
    #    lb = "BB"
    #if lb == "CLUMPY":
    #    lb = "CLU"
    if lb == phtName:
        hd = hd[0]
    labelUse.append(lb)
    handleUse.append(hd)
plt.legend(handleUse, labelUse, loc="upper left", fontsize=16, numpoints=1,
           handletextpad=0.3, handlelength=(4./3.), bbox_to_anchor=(0.02,0.90),
           framealpha=0., edgecolor="white")
plt.savefig("{0}_result.pdf".format(targname), bbox_inches="tight")
plt.close()
print("Best fit plot finished!")

"""
#Plot the corner diagram
em.plot_corner(filename="{0}_triangle.png".format(targname), burnin=burnIn, ps=ps,
               nuisance=nuisance, truths=parTruth,  fraction=fraction,
               quantiles=[psLow/100., psCenter/100., psHigh/100.], show_titles=True,
               title_kwargs={"fontsize": 20})
print("Triangle plot finished!")
"""
