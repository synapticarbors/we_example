import numpy as np
import h5py
import pandas as pd

from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.ticker import NullFormatter


# Potential
def V(r):
    h = 4.0
    r0 = 1.0
    return h*(1.0 - ((r - r0 - 0.5*r0)**2)/(0.5*r0)**2)**2


class WEAnimation(object):

    def __init__(self, step_lim=1000):
        self.step_lim = step_lim
        self.vert_offset = 0.3

        # Trajectory data
        self.bf_traj = self.load_bruteforce_data()
        self.h5we = h5py.File('../we/west.h5', 'r')
        self.we_dist_data, self.we_dist_bins = self.load_we_dist()
        self.bin_bounds = np.linspace(0.5, 2.5, 41).tolist()

        # Distribution data
        self.target_dist_data, self.target_dist_bins, self.bf_dist_data = self.load_bruteforce_dist()

        # Potential data
        self.rpot = np.linspace(0.5, 2.5, 200)
        self.pot = V(self.rpot)
        
        # set up figure and animation
        self.fig = plt.figure(figsize=(6,6))
        self.fig.subplots_adjust(right=0.95, hspace=0.05)
        self.ax_bf = self.fig.add_subplot(311, autoscale_on=False,
                             xlim=(0.5, 2.5), ylim=(-1, 10))


        self.ax_we = self.fig.add_subplot(312, autoscale_on=False,
                             xlim=(0.5, 2.5), ylim=(-1, 10))

        self.ax_dist = self.fig.add_subplot(313, autoscale_on=False,
                             xlim=(0.5, 2.5), ylim=(1E-7, 1))

        self.bf_pot, = self.ax_bf.plot([], [], 'b-', lw=2)
        self.we_pot, = self.ax_we.plot([], [], 'r-', lw=2)
        
        self.target_dist, = self.ax_dist.semilogy([], [], 'k--', lw=1)
        self.bf_dist, = self.ax_dist.semilogy([], [], 'b-', lw=1)
        self.we_dist, = self.ax_dist.semilogy([], [], 'r-', lw=1)

        # Use axis grid to show bin boundaries for WE
        self.ax_we.set_xticks(self.bin_bounds, minor=True)
        self.ax_we.xaxis.grid(True, which='minor', linestyle='-')
        self.ax_we.yaxis.grid(False, which='major', linestyle='-')
        self.ax_we.grid()

        self.bf_particle, = self.ax_bf.plot([], [], 'bo', ms=10)
        self.we_particles, = self.ax_we.plot([], [], 'bo', ms=5) 
        self.time_text = self.ax_bf.text(0.2, 0.85, '', transform=self.ax_bf.transAxes)

        # Customize axis labels
        self.ax_bf.xaxis.set_major_formatter(NullFormatter())
        self.ax_bf.yaxis.set_major_formatter(NullFormatter())
        self.ax_we.xaxis.set_major_formatter(NullFormatter())
        self.ax_we.yaxis.set_major_formatter(NullFormatter())
        self.ax_dist.xaxis.set_major_formatter(NullFormatter())
        self.ax_dist.yaxis.set_major_formatter(NullFormatter())

        self.ax_bf.set_ylabel('$V$', fontsize=16)
        self.ax_we.set_ylabel('$V$', fontsize=16)
        self.ax_dist.set_ylabel('log($P$)', fontsize=16)
        self.ax_dist.set_xlabel('$r$', fontsize=16)

        self.ani = animation.FuncAnimation(self.fig, self.animate, frames=self.step_lim,
                                      interval=10,)# init_func=self.init)

        self.ani.save('we_example.mp4', fps=30,)# extra_args=['-vcodec', 'libx264'])

    def load_bruteforce_data(self):
        with h5py.File('../bruteforce/bruteforce.h5', 'r') as h5bf:
            r = h5bf['coords'][:self.step_lim] 

        bf_traj = np.column_stack((r, V(r) + self.vert_offset))

        return bf_traj

    def load_bruteforce_dist(self):
        with h5py.File('../bruteforce/distribution.h5', 'r') as h5bf:
            d = h5bf['target'][:]
            bins = h5bf['bin_edges'][:]
            devol = h5bf['evol'][:]

        return d, bins[1:] - 0.5*(bins[1] - bins[0]), devol

    def load_we_dist(self):
        with h5py.File('../we/pdist.h5', 'r') as f:
            p = f['histograms'][:]
            b = f['midpoints_0'][:]

        #pcum = pd.rolling_sum(p, window=200, min_periods=0, axis=0)
        pcum = np.cumsum(p, axis=0)
        pcum /= pcum.sum(axis=1)[:, np.newaxis]

        return pcum, b

    def init(self):
        self.bf_particle.set_data([], [])
        self.bf_pot.set_data([], [])
        self.we_pot.set_data([], [])
        self.we_particles.set_data([], [])
        self.time_text.set_text('')

        return self.bf_particle, self.bf_pot, self.we_pot, self.time_text

    def animate(self, i):

        self.bf_pot.set_data(self.rpot, self.pot)
        self.we_pot.set_data(self.rpot, self.pot)
        self.bf_particle.set_data(self.bf_traj[i,0], self.bf_traj[i,1])

        pcoords = self.h5we['iterations']['iter_{:08d}'.format(i+1)]['pcoord'][:,1,0]
        pcoords_vert = V(pcoords) + self.vert_offset
        self.we_particles.set_data(pcoords, pcoords_vert)
        self.time_text.set_text('step = %d' % i)

        self.target_dist.set_data(self.target_dist_bins, self.target_dist_data)
        self.bf_dist.set_data(self.target_dist_bins, self.bf_dist_data[i,:])
        self.we_dist.set_data(self.we_dist_bins, self.we_dist_data[i,:])

        return (self.bf_particle, self.bf_pot, self.we_pot, self.time_text, 
                self.target_dist, self.bf_dist, self.we_dist)

    def show(self):
        plt.show()


if __name__ == '__main__':
    a = WEAnimation(2000)
    #a.show()
