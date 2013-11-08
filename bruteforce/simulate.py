import sys
# Ugly hackish modification of the python path
sys.path.insert(0, '..')
if not any(p in sys.path for p in ['', '.']):
    sys.path.insert(0, '')

import numpy as np

import logging
import os
import time
import argparse
import h5py

import mcsampler

coord_dtype = np.float32


def run(NUM_BLOCKS, STEPS_PER_BLOCK, BLOCKS_PER_DUMP, sim_params):

    print('Setting up logging')
    logging.basicConfig(filename='sim.log', level=logging.DEBUG)
    logging.info('NUM_BLOCKS: {}'.format(NUM_BLOCKS))
    logging.info('STEPS_PER_BLOCK: {}'.format(STEPS_PER_BLOCK))
    logging.info('BLOCKS_PER_DUMP: {}'.format(BLOCKS_PER_DUMP))

    print('Instantiating sampler')
    h = sim_params['h']
    r0 = sim_params['r0']
    dr = sim_params['dr']
    outname = sim_params['outname']
    sampler = mcsampler.Sampler(h, r0, dr, np.random.randint(2**32-1))

    # Setup h5 file
    h5 = h5py.File(outname, 'w')
    h5coords = h5.create_dataset('coords', shape=(NUM_BLOCKS,), compression=9, scaleoffset=2,
            dtype=np.float32, chunks=(BLOCKS_PER_DUMP,))

    # Initial coords
    x = r0

    totblocks = NUM_BLOCKS // BLOCKS_PER_DUMP
    temp_coords = np.zeros((BLOCKS_PER_DUMP,), dtype=coord_dtype)

    print('Starting Simulation')
    for dki, dk in enumerate(xrange(totblocks)):
        t1 = time.time()
        sampler.step(x, temp_coords, BLOCKS_PER_DUMP*STEPS_PER_BLOCK, STEPS_PER_BLOCK)

        h5coords[dki*BLOCKS_PER_DUMP:(dki+1)*BLOCKS_PER_DUMP] = temp_coords[:]
        logging.info('Completed {} of {} steps: {} s'.format(dk,totblocks-1, time.time() - t1))

    h5.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Simulate Dickson Ring Potential')
    parser.add_argument('--nblocks', '-N', dest='nblocks', action='store', type=int,
            help='Number of blocks to run')
    parser.add_argument('--steps', '-s', dest='steps', action='store', type=int,
            help='Steps per block')
    parser.add_argument('--dsize', dest='dsize', action='store', type=int,
            help='Write frequency in number of blocks')

    args = parser.parse_args()

    sim_params = {'h': 4.0,
                  'r0': 1.0,
                  'dr': 0.02,
                  'outname': 'bruteforce.h5'}

    run(args.nblocks, args.steps, args.dsize, sim_params)
