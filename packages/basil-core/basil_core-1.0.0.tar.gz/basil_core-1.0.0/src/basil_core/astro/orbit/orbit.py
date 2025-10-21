'''Python evaluation of c extensions for GW orbit calculations

'''

######## Imports ########
import numpy as np
from ._GW import _beta
from ._GW import _orbital_separation_evolve
from ._kepler import _orbital_period_of_m1_m2_a
from ._GW import _time_of_orbital_shrinkage
from ._GW import _time_to_merge_of_m1_m2_a0
from ._GW import _orbital_period_evolved_GW
from ._DWD_RLOF import _DWD_RLOF_a_of_m1_m2_r1_r2
from ._DWD_RLOF import _DWD_RLOF_P_of_m1_m2_r1_r2
from ._DWD_RLOF import _DWD_r_of_m

######## Declarations ########

__all__ = [
           "beta",
           "orbital_separation_evolve",
           "orbital_period_of_m1_m2_a",
           "time_of_orbital_shrinkage",
           "time_to_merge_of_m1_m2_a0",
           "orbital_period_evolved_GW",
           "DWD_r_of_m",
           "DWD_RLOF_a_of_m1_m2_r1_r2",
           "DWD_RLOF_P_of_m1_m2_r1_r2",
          ]

######## Functions ########

def beta(m1, m2):
    '''Calculate the beta constant from page 8 of Peters (1964)

    Parameters
    ----------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)

    Returns
    -------
    beta_arr `~numpy.ndarray`
        The value of the beta constant
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    return _beta(m1, m2)

def orbital_separation_evolve(m1, m2, a0, t):
    '''Uses Peters(1964) Eq. 5.9 for circular binaries to find separation
        as a function of time

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    a0: `~numpy.ndarray` (npts,)
        Initial orbital separation (meters)
    t: `~numpy.ndarray` (npts,)
        Evolution time (seconds)

    Returns
    -------
    a : `~numpy.ndarray` (npts,)
        Evolved orbital separation (meters)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a0 ##
    if not isinstance(a0, np.ndarray):
        raise TypeError("a0 should be a numpy array, but is ", type(a0))
    if len(a0.shape) != 1:
        raise RuntimeError("a0 should be 1D array, but is ", a0.shape)
    ## Check t ##
    if not isinstance(t, np.ndarray):
        raise TypeError("t should be a numpy array, but is ", type(t))
    if len(t.shape) != 1:
        raise RuntimeError("t should be 1D array, but is ", t.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a0.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a0.size = %d"%(
            m1.size, a0.size))
    if not (m1.size == t.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, t.size = %d"%(
            m1.size, t.size))
    return _orbital_separation_evolve(m1, m2, a0, t)

def orbital_period_of_m1_m2_a(m1, m2, a):
    '''Calculate orbital period using Kepler's equations

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    a: `~numpy.ndarray` (npts,)
        Orbital separation (meters)

    Returns
    -------
    P : `~numpy.ndarray` (npts,)
        Orbital period (seconds)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a ##
    if not isinstance(a, np.ndarray):
        raise TypeError("a should be a numpy array, but is ", type(a))
    if len(a.shape) != 1:
        raise RuntimeError("a should be 1D array, but is ", a.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a.size = %d"%(
            m1.size, a.size))
    return _orbital_period_of_m1_m2_a(m1, m2, a)

def time_of_orbital_shrinkage(m1, m2, a0, af):
    '''Finds time at which a binary will have a particular separation after
        evolving due to GW radiation

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    a0: `~numpy.ndarray` (npts,)
        Initial orbital separation (meters)
    af: `~numpy.ndarray` (npts,)
        Final orbital separation (meters)

    Returns
    -------
    P : `~numpy.ndarray` (npts,)
        Orbital period (seconds)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a ##
    if not isinstance(a0, np.ndarray):
        raise TypeError("a0 should be a numpy array, but is ", type(a0))
    if len(a0.shape) != 1:
        raise RuntimeError("a0 should be 1D array, but is ", a0.shape)
    ## Check af ##
    if not isinstance(af, np.ndarray):
        raise TypeError("af should be a numpy array, but is ", type(af))
    if len(af.shape) != 1:
        raise RuntimeError("af should be 1D array, but is ", af.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a0.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a0.size = %d"%(
            m1.size, a0.size))
    if not (m1.size == af.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, af.size = %d"%(
            m1.size, af.size))
    return _time_of_orbital_shrinkage(m1, m2, a0, af)

def time_to_merge_of_m1_m2_a0(m1, m2, a0):
    '''Use Peters(1964) Eq. 5.10 to determine the merger of a circular
        DWD binary from time of SRF

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    a0: `~numpy.ndarray` (npts,)
        Initial orbital separation (meters)

    Returns
    -------
    P : `~numpy.ndarray` (npts,)
        Orbital period (seconds)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a ##
    if not isinstance(a0, np.ndarray):
        raise TypeError("a0 should be a numpy array, but is ", type(a0))
    if len(a0.shape) != 1:
        raise RuntimeError("a0 should be 1D array, but is ", a0.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a0.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a0.size = %d"%(
            m1.size, a0.size))
    return _time_to_merge_of_m1_m2_a0(m1, m2, a0)

def orbital_period_evolved_GW(m1, m2, a0, t):
    ''' Calculate the obrital period after GW evolution

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    a0: `~numpy.ndarray` (npts,)
        Initial orbital separation
    t: `~numpy.ndarray` (npts,)
        Evolution time (seconds)

    Returns
    -------
    P : `~numpy.ndarray` (npts,)
        Evolved orbital period (seconds)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check a0 ##
    if not isinstance(a0, np.ndarray):
        raise TypeError("a0 should be a numpy array, but is ", type(a0))
    if len(a0.shape) != 1:
        raise RuntimeError("a0 should be 1D array, but is ", a0.shape)
    ## Check t ##
    if not isinstance(t, np.ndarray):
        raise TypeError("t should be a numpy array, but is ", type(t))
    if len(t.shape) != 1:
        raise RuntimeError("t should be 1D array, but is ", t.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == a0.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, a0.size = %d"%(
            m1.size, a0.size))
    if not (m1.size == t.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, t.size = %d"%(
            m1.size, t.size))
    return _orbital_period_evolved_GW(m1, m2, a0, t)

def DWD_r_of_m(m):
    ''' Calculate the radius of a white dwarf (in solar radii)
    Taken from Eq. 91 in Hurley et al. (2000) from Eq. 17 in Tout et al. (1997)

    Would love to output in meters, but it's not my equation.

    Paramters
    ---------
    m: `~numpy.ndarray` (npts,)
        WD masses (Kg)

    Returns
    -------
    r: `~numpy.ndarray` (npts,)
        WD radii (RSUN)
    '''
    #### Check inputs ####
    ## Check m ##
    if not isinstance(m, np.ndarray):
        raise TypeError("m should be a numpy array, but is ", type(m))
    if len(m.shape) != 1:
        raise RuntimeError("m should be 1D array, but is ", m.shape)
    return _DWD_r_of_m(m)

def DWD_RLOF_a_of_m1_m2_r1_r2(m1, m2, r1, r2):
    ''' Calculate the separation of Roche Lobe overflow

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    r1 : `~numpy.ndarray` (npts,)
        Radius of primary WD (meters)
    r2 : `~numpy.ndarray` (npts,)
        Radius of secondary WD (meters)

    Returns
    -------
    a : `~numpy.ndarray` (npts,)
        Separation of RLOF (m)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check r1 ##
    if not isinstance(r1, np.ndarray):
        raise TypeError("r1 should be a numpy array, but is ", type(r1))
    if len(r1.shape) != 1:
        raise RuntimeError("r1 should be 1D array, but is ", r1.shape)
    ## Check r2 ##
    if not isinstance(r2, np.ndarray):
        raise TypeError("r2 should be a numpy array, but is ", type(r2))
    if len(r2.shape) != 1:
        raise RuntimeError("r2 should be 1D array, but is ", r2.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == r1.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, r1.size = %d"%(
            m1.size, r1.size))
    if not (m1.size == r2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, r2.size = %d"%(
            m1.size, r2.size))
    return _DWD_RLOF_a_of_m1_m2_r1_r2(m1, m2, r1, r2)

def DWD_RLOF_P_of_m1_m2_r1_r2(m1, m2, r1, r2):
    ''' Calculate the orbital period of the separation at which
        Roche Lobe overflow begins

    Paramters
    ---------
    m1: `~numpy.ndarray` (npts,)
        First set of masses (Kg)
    m2: `~numpy.ndarray` (npts,)
        Second set of masses (Kg)
    r1 : `~numpy.ndarray` (npts,)
        Radius of primary WD (meters)
    r2 : `~numpy.ndarray` (npts,)
        Radius of secondary WD (meters)

    Returns
    -------
    P : `~numpy.ndarray` (npts,)
        Orbital period of RLOF (seconds)
    '''
    #### Check inputs ####
    ## Check m1 ##
    if not isinstance(m1, np.ndarray):
        raise TypeError("m1 should be a numpy array, but is ", type(m1))
    if len(m1.shape) != 1:
        raise RuntimeError("m1 should be 1D array, but is ", m1.shape)
    ## Check m2 ##
    if not isinstance(m2, np.ndarray):
        raise TypeError("m2 should be a numpy array, but is ", type(m2))
    if len(m2.shape) != 1:
        raise RuntimeError("m2 should be 1D array, but is ", m2.shape)
    ## Check r1 ##
    if not isinstance(r1, np.ndarray):
        raise TypeError("r1 should be a numpy array, but is ", type(r1))
    if len(r1.shape) != 1:
        raise RuntimeError("r1 should be 1D array, but is ", r1.shape)
    ## Check r2 ##
    if not isinstance(r2, np.ndarray):
        raise TypeError("r2 should be a numpy array, but is ", type(r2))
    if len(r2.shape) != 1:
        raise RuntimeError("r2 should be 1D array, but is ", r2.shape)
    ## Check dimensions ##
    if not (m1.size == m2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, m2.size = %d"%(
            m1.size, m2.size))
    if not (m1.size == r1.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, r1.size = %d"%(
            m1.size, r1.size))
    if not (m1.size == r2.size):
        raise RuntimeError("Dimension mismatch: m1.size = %d, r2.size = %d"%(
            m1.size, r2.size))
    return _DWD_RLOF_P_of_m1_m2_r1_r2(m1, m2, r1, r2)
