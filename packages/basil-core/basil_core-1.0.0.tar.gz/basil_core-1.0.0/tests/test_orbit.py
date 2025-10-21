#!/usr/env/bin python3

######## Setup ########
import numpy as np
import time

from astropy import constants as const

######## Globals ########
MSUN = const.M_sun.value
RSUN = const.R_sun.value
G = const.G.value
c = const.c.value
SEC_PER_DAY = 86400
CHANDRASEKHAR_LIMIT = 1.4


######## Functions ########

def m1m2_grid(m1_min=1., m1_max=50., m2_min=1., m2_max=50., n=10):
    m1 = np.linspace(m1_min, m1_max, n)
    m2 = np.linspace(m2_min, m2_max, n)
    m1, m2 = np.meshgrid(m1, m2)
    m1, m2 = m1.flatten(), m2.flatten()
    m1, m2 = m1*MSUN, m2*MSUN
    return m1, m2

def a0t_grid(a0_min=1., a0_max=100.,t_min=1.,t_max=100., n=10):
    a0 = np.linspace(a0_min, a0_max, n)
    t = np.linspace(t_min, t_max, n)
    a0, t = np.meshgrid(a0, t)
    a0, t = a0.flatten(), t.flatten()
    a0 = a0*RSUN
    t = t*SEC_PER_DAY
    return a0, t

def m1m2a0t_data(n=10):
    m1, m2 = m1m2_grid(n=n)
    a0, t = a0t_grid(n=n)
    return m1, m2, a0, t

def numpy_rad_WD(M):
    R_NS = 1.4e-5*np.ones(len(M))
    M_CH = CHANDRASEKHAR_LIMIT * MSUN
    M_CH_M_2_3 = (M_CH/M)**(2/3)
    M_M_CH_2_3 = (M/M_CH)**(2/3)
    A = 0.0115 * np.sqrt(M_CH_M_2_3 - M_M_CH_2_3)
    rad = np.max(np.array([R_NS, A]),axis=0)
    rad *= RSUN
    return rad
    
def m1m2r1r2_data(n=10):
    m1, m2 = m1m2_grid(m1_max=CHANDRASEKHAR_LIMIT,m2_max=CHANDRASEKHAR_LIMIT,n=n)
    r1, r2 = numpy_rad_WD(m1), numpy_rad_WD(m2)
    return m1, m2, r1, r2

######## C extensions ########

def cext_beta(n=100):
    from basil_core.astro.orbit import beta
    # Get data
    m1, m2 = m1m2_grid(n=n)
    t0 = time.time()
    beta_arr = beta(m1, m2)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return beta_arr

def cext_orbital_separation_evolve(n=100):
    from basil_core.astro.orbit import orbital_separation_evolve
    m1, m2, a0, t = m1m2a0t_data(n=n)
    t0 = time.time()
    a_arr = orbital_separation_evolve(m1, m2, a0, t)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return a_arr

def cext_orbital_period_of_m1_m2_a(n=100):
    from basil_core.astro.orbit import orbital_period_of_m1_m2_a
    m1, m2, a, t = m1m2a0t_data(n=n)
    t0 = time.time()
    P_arr = orbital_period_of_m1_m2_a(m1, m2, a)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return P_arr

def cext_time_of_orbital_shrinkage(n=100):
    from basil_core.astro.orbit import time_of_orbital_shrinkage
    m1, m2, a0, t = m1m2a0t_data(n=n)
    af = a0/2
    t0 = time.time()
    t_arr = time_of_orbital_shrinkage(m1, m2, a0, af)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return t_arr

def cext_time_to_merge_of_m1_m2_a0(n=100):
    from basil_core.astro.orbit import time_to_merge_of_m1_m2_a0
    m1, m2, a0, t = m1m2a0t_data(n=n)
    t0 = time.time()
    t_arr = time_to_merge_of_m1_m2_a0(m1, m2, a0)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return t_arr

def cext_orbital_period_evolved_GW(n=100):
    from basil_core.astro.orbit import orbital_period_evolved_GW
    m1, m2, a0, t = m1m2a0t_data(n=n)
    t0 = time.time()
    P_arr = orbital_period_evolved_GW(m1, m2, a0, t)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return P_arr

def cext_DWD_r_of_m(n=100):
    from basil_core.astro.orbit import DWD_r_of_m
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    t0 = time.time()
    a_arr = DWD_r_of_m(m1)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return a_arr

def cext_DWD_RLOF_a_of_m1_m2_r1_r2(n=100):
    from basil_core.astro.orbit import DWD_RLOF_a_of_m1_m2_r1_r2
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    t0 = time.time()
    a_arr = DWD_RLOF_a_of_m1_m2_r1_r2(m1, m2, r1, r2)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return a_arr

def cext_DWD_RLOF_P_of_m1_m2_r1_r2(n=100):
    from basil_core.astro.orbit import DWD_RLOF_P_of_m1_m2_r1_r2
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    t0 = time.time()
    P_arr = DWD_RLOF_P_of_m1_m2_r1_r2(m1, m2, r1, r2)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return P_arr


######## Numpy functions ########

def numpy_beta(n=100):
    m1, m2 = m1m2_grid(n=n)
    t0 = time.time()
    const = ((64 / 5) * G**3) * (c**-5)
    beta_arr = const * m1 * m2 * (m1 + m2)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return beta_arr

def numpy_orbital_separation_evolve(n=100):
    m1, m2, a0, t = m1m2a0t_data(n=n)
    t0 = time.time()
    const = ((64 / 5) * G**3) * (c**-5)
    beta_arr = const * m1 * m2 * (m1 + m2)
    a_arr = np.sqrt(np.sqrt((a0 ** 4) - (4 * beta_arr * t)))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return a_arr

def numpy_orbital_period_of_m1_m2_a(n=100):
    m1, m2, a, t = m1m2a0t_data(n=n)
    t0 = time.time()
    P_arr = np.sqrt(4 * np.pi**2 * a**3 / (G * (m1 + m2)))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return P_arr

def numpy_time_of_orbital_shrinkage(n=100):
    m1, m2, a0, t = m1m2a0t_data(n=n)
    af = a0/2
    t0 = time.time()
    const = ((64 / 5) * G**3) * (c**-5)
    beta_arr = const * m1 * m2 * (m1 + m2)
    t_arr = (a0 ** 4 - af ** 4) / 4 / beta_arr
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return t_arr

def numpy_time_to_merge_of_m1_m2_a0(n=100):
    m1, m2, a0, t = m1m2a0t_data(n=n)
    t0 = time.time()
    const = ((64 / 5) * G**3) * (c**-5)
    beta_arr = const * m1 * m2 * (m1 + m2)
    t_arr = (a0 ** 4) / 4 / beta_arr
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return t_arr

def numpy_orbital_period_evolved_GW(n=100):
    m1, m2, a0, t = m1m2a0t_data(n=n)
    t0 = time.time()
    const = ((64 / 5) * G**3) * (c**-5)
    beta_arr = const * m1 * m2 * (m1 + m2)
    a_arr = np.sqrt(np.sqrt((a0 ** 4) - (4 * beta_arr * t)))
    P_arr = np.sqrt(4 * np.pi**2 * a_arr**3 / (G * (m1 + m2)))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return P_arr

def numpy_DWD_r_of_m(n=100):
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    t0 = time.time()
    a_arr = numpy_rad_WD(m1)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return a_arr

def numpy_DWD_RLOF_a_of_m1_m2_r1_r2(n=100):
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    t0 = time.time()
    mA = np.where(m1>m2, m1, m2)
    mB = np.where(m1>m2, m2, m1)
    rB = np.where(m1>m2, r2, r1)
    q = mB/mA
    denominator = 0.49 * q**(2/3)
    numerator = 0.6 * q**(2/3) + np.log(1 + q**(1/3))
    a_arr = numerator * rB / denominator
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return a_arr

def numpy_DWD_RLOF_P_of_m1_m2_r1_r2(n=100):
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    t0 = time.time()
    mA = np.where(m1>m2, m1, m2)
    mB = np.where(m1>m2, m2, m1)
    rB = np.where(m1>m2, r2, r1)
    q = mB/mA
    denominator = 0.49 * q**(2/3)
    numerator = 0.6 * q**(2/3) + np.log(1 + q**(1/3))
    a_arr = numerator * rB / denominator
    P_arr = np.sqrt(4 * np.pi**2 * a_arr**3 / (G * (m1 + m2)))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return P_arr

######## Tests ########
def beta_test(n=100):
    print("Beta test")
    B1 = cext_beta(n=n)
    B2 = numpy_beta(n=n)
    assert np.allclose(B1, B2)
    print("  pass!")

def orbital_separation_evolve_test(n=100):
    print("Orbital Separation test")
    a1 = cext_orbital_separation_evolve(n=n)
    a2 = numpy_orbital_separation_evolve(n=n)
    assert np.allclose(a1, a2)
    print("  pass!")

def orbital_period_of_m1_m2_a_test(n=100):
    print("Orbital Period test")
    P1 = cext_orbital_period_of_m1_m2_a(n=n)
    P2 = numpy_orbital_period_of_m1_m2_a(n=n)
    assert np.allclose(P1, P2)
    print("  pass!")

def time_of_orbital_shrinkage_test(n=100):
    print("Orbital Shrinkage test")
    t1 = cext_time_of_orbital_shrinkage(n=n)
    t2 = numpy_time_of_orbital_shrinkage(n=n)
    assert np.allclose(t1, t2)
    print("  pass!")

def time_to_merge_of_m1_m2_a0_test(n=100):
    print("Time to merger test")
    t1 = cext_time_to_merge_of_m1_m2_a0(n=n)
    t2 = numpy_time_to_merge_of_m1_m2_a0(n=n)
    assert np.allclose(t1, t2)
    print("  pass!")

def orbital_period_evolved_GW_test(n=100):
    print("Orbital period evolve test")
    P1 = cext_orbital_period_evolved_GW(n=n)
    P2 = numpy_orbital_period_evolved_GW(n=n)
    assert np.allclose(P1, P2)
    print("  pass!")

def DWD_r_of_m_test(n=100):
    print("WD radius test")
    a1 = cext_DWD_r_of_m(n=n)
    a2 = numpy_DWD_r_of_m(n=n)
    assert np.allclose(a1, a2)
    print("  pass!")

def DWD_RLOF_a_of_m1_m2_r1_r2_test(n=100):
    print("DWD Roche-lobe separation test")
    a1 = cext_DWD_RLOF_a_of_m1_m2_r1_r2(n=n)
    a2 = numpy_DWD_RLOF_a_of_m1_m2_r1_r2(n=n)
    assert np.allclose(a1, a2)
    print("  pass!")

def DWD_RLOF_P_of_m1_m2_r1_r2_test(n=100):
    print("DWD Roche-lobe period test")
    P1 = cext_DWD_RLOF_P_of_m1_m2_r1_r2(n=n)
    P2 = numpy_DWD_RLOF_P_of_m1_m2_r1_r2(n=n)
    assert np.allclose(P1, P2)
    print("  pass!")



######## All Tests ########

def all_test(**kwargs):
    beta_test(**kwargs)
    orbital_separation_evolve_test(**kwargs)
    orbital_period_of_m1_m2_a_test(**kwargs)
    time_of_orbital_shrinkage_test(**kwargs)
    time_to_merge_of_m1_m2_a0_test(**kwargs)
    orbital_period_evolved_GW_test(**kwargs)
    DWD_r_of_m_test(**kwargs)
    DWD_RLOF_a_of_m1_m2_r1_r2_test(**kwargs)
    DWD_RLOF_P_of_m1_m2_r1_r2_test(**kwargs)

######## Main ########
def main():
    n = int(1e3)
    all_test(n=n)
    return

######## Execution ########
if __name__ == "__main__":
    main()

