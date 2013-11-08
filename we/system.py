from __future__ import division, print_function
__metaclass__ = type

import sys
sys.path.insert(0, '..')

import time
import os
import numpy as np

import west
from west.propagators import WESTPropagator
from west import Segment, WESTSystem
from westpa.binning import RectilinearBinMapper 

import mcsampler

import logging
log = logging.getLogger(__name__)
log.debug('loading module %r' % __name__)

pcoord_dtype = np.float32


class MonteCarloPropagator(WESTPropagator):

    def __init__(self, rc=None):
        super(MonteCarloPropagator, self).__init__(rc)

        rc = self.rc.config['west','montecarlo']
        self.nsteps = rc.get('blocks_per_iteration', 2)
        self.nsubsteps = rc.get('steps_per_block')

        h = 5.0 
        r0 = 1.0
        dr = 0.02

        self.sampler = mcsampler.Sampler(h, r0, dr, np.random.randint(2**32-1))

    def get_pcoord(self, state):
        pcoord = None
        if state.label == 'initA':
            pcoord = [1.0,]
        elif state.label == 'initB':
            pcoord = [2.0,]

        state.pcoord = pcoord

    def propagate(self, segments):

        for segment in segments:
            starttime = time.time()
            new_pcoords = np.empty((self.nsteps, 1), dtype=pcoord_dtype)
            new_pcoords[0,0] = segment.pcoord[0,0]
            x = new_pcoords[0,0]

            for istep in xrange(1, self.nsteps):
                x = self.sampler.step_simple(x, self.nsubsteps)
                new_pcoords[istep,0] = x

            segment.pcoord = new_pcoords[...]
            segment.status = Segment.SEG_STATUS_COMPLETE
            segment.walltime = time.time() - starttime

        return segments


class System(WESTSystem):

    def initialize(self):

        rc = self.rc.config['west', 'system']

        self.pcoord_ndim = 1
        self.pcoord_len = 2
        self.pcoord_dtype = pcoord_dtype
        self.target_count = rc.get('target_count')

        bin_bounds = [-float('inf')] + np.linspace(0.5, 2.5, 41).tolist() + [float('inf')]
        self.bin_mapper = RectilinearBinMapper([bin_bounds]) 
        self.bin_target_counts = np.zeros((len(bin_bounds),), dtype=np.int_)
        self.bin_target_counts[...] = self.target_count

