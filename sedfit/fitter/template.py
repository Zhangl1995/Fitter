import numpy as np
from sklearn.neighbors import KDTree
from scipy.interpolate import splev

class Template(object):
    """
    This is the object of a model template.
    """

    def __init__(self, tckList, kdTree, parList, modelInfo={}, parFormat=[], readMe=""):
        self.__tckList   = tckList
        self.__kdTree    = kdTree
        self.__parList   = parList
        self.__modelInfo = modelInfo
        self.__parFormat = parFormat
        self._readMe    = readMe

    def __call__(self, x, pars):
        """
        Return the interpolation result of the template nearest the input
        parameters.
        """
        x = np.array(x)
        ind = np.squeeze(self.__kdTree.query(np.atleast_2d(pars), return_distance=False))
        tck = self.__tckList[ind]
        return splev(x, tck)

    def get_nearestParameters(self, pars):
        """
        Return the nearest template parameters to the input parameters.
        """
        ind = np.squeeze(self.__kdTree.query(np.atleast_2d(pars), return_distance=False))
        return self.__parList[ind]

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, dict):
        self.__dict__ = dict

    def get_parList(self):
        return self.__parList

    def get_modelInfo(self):
        return self.__modelInfo

    def get_parFormat(self):
        return self.__parFormat

    def readme(self):
        return self._readMe