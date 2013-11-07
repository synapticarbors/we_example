import numpy as np
cimport numpy as np
cimport cython

from cpython.mem cimport PyMem_Malloc, PyMem_Free
from libc.math cimport exp

DTYPE = np.float32
ctypedef np.float32_t DTYPE_t

cdef extern from "randomkit.h": 
    ctypedef struct rk_state: 
        unsigned long key[624] 
        int pos 
        int has_gauss 
        double gauss 
    void rk_seed(unsigned long seed, rk_state *state) 
    double rk_gauss(rk_state *state)
    double rk_double(rk_state *state)


@cython.cdivision(True)
cdef double V(double r, double r0, double h):
    return h*(1.0 - ((r - r0 - 0.5*r0)**2)/(0.5*r0)**2)**2


cdef class Sampler:
    cdef:
        double h, r0, dr
        rk_state *rng_state

    def __cinit__(self, double h, double r0, double dr, unsigned long seed):
        self.rng_state = <rk_state*>PyMem_Malloc(sizeof(rk_state))

    def __dealloc__(self): 
        if self.rng_state != NULL: 
            PyMem_Free(self.rng_state) 
            self.rng_state = NULL

    def __init__(self, double h, double r0, double dr, unsigned long seed):
        self.h = h
        self.r0 = r0
        self.dr = dr

        rk_seed(seed, self.rng_state)


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.cdivision(True)
    def step(self, double r_init, np.float32_t[::1] traj, int steps, int save_freq):
        cdef:
            double r_curr, r_trial, v_curr, v_trial
            unsigned int k
            unsigned int ti = 0

        r_curr = r_init
        v_curr = V(r_curr, self.r0, self.h)

        for k in xrange(steps):
            r_trial = r_curr + self.dr * (1.0 - 2*rk_double(self.rng_state))
            v_trial = V(r_trial, self.r0, self.h)

            if v_trial < v_curr:
                r_curr = r_trial
                v_curr = v_trial
            else:
                if exp(-(v_trial - v_curr)) > rk_double(self.rng_state):
                    r_curr = r_trial
                    v_curr = v_trial

            if k % save_freq == 0:
                traj[ti] = r_curr
                ti += 1

    def step_simple(self, double r_init, int steps):
        cdef:
            double r_curr, r_trial, v_curr, v_trial
            unsigned int k

        r_curr = r_init
        v_curr = V(r_curr, self.r0, self.h)

        for k in xrange(steps):
            r_trial = r_curr + self.dr * rk_gauss(self.rng_state)
            v_trial = V(r_trial, self.r0, self.h)

            if v_trial < v_curr:
                r_curr = r_trial
                v_curr = v_trial
            else:
                if exp(-(v_trial - v_curr)) > rk_double(self.rng_state):
                    r_curr = r_trial
                    v_curr = v_trial

        return r_curr
