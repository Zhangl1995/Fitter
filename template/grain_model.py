#This code generate the KDTree template file that can be directly used.

import numpy as np
import matplotlib.pyplot as plt
import cPickle as pickle
from sklearn.neighbors import KDTree
from scipy.interpolate import splrep, splev
from sedfit.fitter.template import Template

modelDir = "/Users/jinyi/Work/mcmc/Fitter/template/grain_models/"
silNameList = ["sil", "amo4"]
graNameList = ["grap"]
sizeList = np.arange(0.1, 1.6, 0.1)
silTList = np.arange(len(silNameList)) #The types of silicate dust.
graTList = np.arange(len(graNameList)) #The types of graphite dust.

#Obtain the silicate template interpolated list
tckSilList = []
parSilList = []
for nsil in silTList:
    for sz in sizeList:
        tmplDir = modelDir + "{0}/qsohst_{0}_a{1}_dat".format(silNameList[nsil], sz)
        modelSil = np.loadtxt(tmplDir)
        wave  = modelSil[:, 0]
        kappa = modelSil[:, 1]
        tck = splrep(wave, kappa)
        tckSilList.append(tck)
        parSilList.append([nsil, sz])
kdtSil = KDTree(parSilList)
print("Silicate dust interpolation finishes!")
modelInfo = {
    "type": silTList, #Silicate dust type
    "size": sizeList,
    "wavelength": wave,
}
parFormat = ["type", "size"]
readMe = '''
This silicate template is generated by Yanxia using Mie theory.
The interpolation is tested well!
'''
silDict = {
    "tckList": tckSilList,
    "kdTree": kdtSil,
    "parList": parSilList,
    "modelInfo": modelInfo,
    "parFormat": parFormat,
    "readMe": readMe
}

#Obtain the graphite template interpolated list
tckGraList = []
parGraList = []
for ngra in graTList:
    for sz in sizeList:
        tmplDir = modelDir + "{0}/qsohst_{0}_a{1}_dat".format(graNameList[ngra], sz)
        modelGra = np.loadtxt(tmplDir)
        wave  = modelGra[:, 0]
        kappa = modelGra[:, 1]
        tck = splrep(wave, kappa)
        tckGraList.append(tck)
        parGraList.append([ngra, sz])
kdtGra = KDTree(parGraList)
print("Graphite dust interpolation finishes!")
modelInfo = {
    "type": graTList, #Silicate dust type
    "size": sizeList,
    "wavelength": wave,
}
parFormat = ["type", "size"]
readMe = '''
This graphite template is generated by Yanxia using Mie theory.
The interpolation is tested well!
'''
graDict = {
    "tckList": tckGraList,
    "kdTree": kdtGra,
    "parList": parGraList,
    "modelInfo": modelInfo,
    "parFormat": parFormat,
    "readMe": readMe
}

#Save the template
templateReadMe = '''
This template file consists two template dicts for silicate and graphite dust
grain. Each of the dicts can be used as input of the Template class in sedfit
package.
'''
dustModel = {
    "Silicate": silDict,
    "Graphite": graDict,
    "readMe": templateReadMe
}
fp = open("/Users/jinyi/Work/mcmc/Fitter/template/dust_grain_kdt.tmplt", "w")
pickle.dump(dustModel, fp)
fp.close()

##Test the KDTree and the interpolation
#For the astronomical silicate
for sz in sizeList:
    modelSil = np.loadtxt(modelDir+"sil/qsohst_sil_a{0}_dat".format(sz))
    wave0  = modelSil[:, 0]
    kappa0 = modelSil[:, 1]
    t = Template(**silDict)
    par = [0, sz-0.01]
    kappa = t(wave0, par)
    print max(abs(kappa-kappa0))
    plt.plot(wave0, kappa, label="{0:.1f}".format(sz))
    plt.plot(wave0, kappa0, ":r")
plt.xscale("log")
plt.yscale("log")
plt.legend(loc="best", fontsize=10)
plt.title("{0}".format("Astronomy Silicate"), fontsize=24)
plt.savefig("dust_sil.png")
plt.show()
#For the amorphous oliven
for sz in sizeList:
    modelAmo = np.loadtxt(modelDir+"amo4/qsohst_amo4_a{0}_dat".format(sz))
    wave0  = modelAmo[:, 0]
    kappa0 = modelAmo[:, 1]
    t = Template(**silDict)
    par = [1, sz-0.01]
    kappa = t(wave0, par)
    print max(abs(kappa-kappa0))
    plt.plot(wave0, kappa, label="{0:.1f}".format(sz))
    plt.plot(wave0, kappa0, ":r")
plt.xscale("log")
plt.yscale("log")
plt.legend(loc="best", fontsize=10)
plt.title("{0}".format("Amorphous Olive"), fontsize=24)
plt.savefig("dust_amo4.png")
plt.show()
#For the graphite
for sz in sizeList:
    modelGra = np.loadtxt(modelDir+"grap/qsohst_grap_a{0}_dat".format(sz))
    wave0  = modelGra[:, 0]
    kappa0 = modelGra[:, 1]
    t = Template(**graDict)
    par = [0, sz-0.01]
    kappa = t(wave0, par)
    print max(abs(kappa-kappa0))
    plt.plot(wave0, kappa, label="{0:.1f}".format(sz))
    plt.plot(wave0, kappa0, ":r")
plt.xscale("log")
plt.yscale("log")
plt.legend(loc="best", fontsize=10)
plt.title("{0}".format("Graphite"), fontsize=24)
plt.savefig("dust_grap.png")
plt.show()