from __future__ import print_function
import matplotlib
matplotlib.use("Agg")
import sys
import types
import corner
import importlib
import numpy as np
from sedfit.fitter import basicclass as bc
from sedfit import model_functions as sedmf
from sedfit import fit_functions   as sedff
from sedfit.fitter import mcmc
from emcee.utils import MPIPool


# Initialize the MPI-based pool used for parallelization.
pool = MPIPool()

if not pool.is_master():
    # Wait for instructions from the master process.
    pool.wait()
    sys.exit(0)

#The code starts#
#---------------#
print("############################")
print("# Galaxy SED Fitter starts #")
print("############################")
print("\n")

#Load the input info#
#-------------------#
if len(sys.argv) > 1:
    moduleName = sys.argv[1]
else:
    moduleName = "input_emcee"
print("Input module: {0}".format(moduleName))
inputModule = importlib.import_module(moduleName)

#Input SED data#
#--------------#
sedData = inputModule.sedData

#Input model#
#-----------#
sedModel = inputModule.sedModel
parAllList = inputModule.parAllList
ndim = len(parAllList)

#Fit with MCMC#
#---------------#
emceeDict = inputModule.emceeDict
imSampler = emceeDict["sampler"]
nwalkers  = emceeDict["nwalkers"]
ntemps    = emceeDict["ntemps"]
iteration = emceeDict["iteration"]
iStep     = emceeDict["iter-step"]
ballR     = emceeDict["ball-r"]
ballT     = emceeDict["ball-t"]
rStep     = emceeDict["run-step"]
burnIn    = emceeDict["burn-in"]
thin      = emceeDict["thin"]
threads   = emceeDict["threads"]
printFrac = emceeDict["printfrac"]
ppDict   = inputModule.ppDict
psLow    = ppDict["low"]
psCenter = ppDict["center"]
psHigh   = ppDict["high"]

print("#--------------------------------#")
print("emcee Info:")
for keys in emceeDict.keys():
    print("{0}: {1}".format(keys, emceeDict[keys]))
print("#--------------------------------#")
modelUnct = inputModule.modelUnct
em = mcmc.EmceeModel(sedData, sedModel, modelUnct, imSampler)

if imSampler == "PTSampler":
    p0 = np.zeros((ntemps, nwalkers, ndim))
    for loop_t in range(ntemps):
        for loop_w in range(nwalkers):
            p0[loop_t, loop_w, :] = em.from_prior()
    sampler = em.PTSampler(ntemps, nwalkers, pool=pool)
elif imSampler == "EnsembleSampler":
    p0 = [em.from_prior() for i in range(nwalkers)]
    sampler = em.EnsembleSampler(nwalkers, pool=pool)
else:
    raise RuntimeError("Cannot recognise the sampler '{0}'!".format(imSampler))


#Burn-in 1st
print( "\n{:*^35}".format(" {0}th iteration ".format(0)) )
pos, lnprob, state = em.run_mcmc(p0, iterations=iStep, printFrac=printFrac, thin=thin)
em.diagnose()
pmax = em.p_logl_max()
em.print_parameters(parAllList, burnin=50)

#Burn-in rest iteration
for i in range(iteration-1):
    print( "\n{:*^35}".format(" {0}th iteration ".format(i+1)) )
    em.reset()
    ratio = ballR * ballT**i
    print("-- P1 ball radius ratio: {0:.3f}".format(ratio))
    p1 = em.p_ball(pmax, ratio=ratio)
    em.run_mcmc(p1, iterations=iStep, printFrac=printFrac, thin=thin)
    em.diagnose()
    pmax = em.p_logl_max()
    em.print_parameters(parAllList, burnin=50)

#Run MCMC
print( "\n{:*^35}".format(" Final Sampling ") )
em.reset()
ratio = ballR * ballT**i
print("-- P1 ball radius ratio: {0:.3f}".format(ratio))
p1 = em.p_ball(pmax, ratio=ratio)
em.run_mcmc(p1, iterations=rStep, printFrac=printFrac, thin=thin)
em.diagnose()
em.print_parameters(parAllList, burnin=burnIn, low=psLow, center=psCenter, high=psHigh)

#Close the pools
pool.close()

#Post process
targname = inputModule.targname
em.plot_chain(filename="{0}_chain.png".format(targname), truths=parAllList)
em.plot_corner(filename="{0}_triangle.png".format(targname), burnin=burnIn, truths=parAllList,
               quantiles=[psLow/100., psCenter/100., psHigh/100.], show_titles=True,
               title_kwargs={"fontsize": 24})
em.plot_fit(filename="{0}_result.png".format(targname), truths=parAllList, burnin=burnIn,
            low=psLow, center=psCenter, high=psHigh)
em.Save_Samples("{0}_samples.txt".format(targname), burnin=0)
print("Post-processed!")
