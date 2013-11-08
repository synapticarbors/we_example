import numpy as np
import h5py

bins = np.arange(0, 3, 0.02)
n_evol = 2000

with h5py.File('bruteforce.h5', 'r') as h5:
    coords = h5['coords'][:]

with h5py.File('distribution.h5', 'w') as h5out:
    h, bin_edges = np.histogram(coords, bins=bins)
    h.dtype = np.float64
    ii = np.nonzero(h)
    h[ii] = 1.0*h[ii]/h.sum()
    h5out.create_dataset('target', data=h)
    h5out.create_dataset('bin_edges', data=bin_edges)

    hevol = np.zeros((n_evol, h.shape[0]))
    for k in xrange(n_evol):
        he, _ = np.histogram(coords[:k], bins=bins)
        he.dtype = np.float64
        ii = np.nonzero(he)
        he[ii] = 1.0*he[ii]/he.sum()

        hevol[k,:] = he

    h5out.create_dataset('evol', data=hevol)




