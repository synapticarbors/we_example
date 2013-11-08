import numpy as np
import h5py

from matplotlib import pyplot as plt
from matplotlib import animation


# Potential
def V(r):
    h = 5.0
    r0 = 1.0
    return h*(1.0 - ((r - r0 - 0.5*r0)**2)/(0.5*r0)**2)**2


# Set up data

step_lim = 2000
vert_offset = 0.3

# Brute force
h5bf = h5py.File('../bruteforce/bruteforce.h5', 'r')
r = h5bf['coords'][:step_lim] 
bf_traj = np.column_stack((r, V(r) + vert_offset))

# Weighted Ensemble
h5we = h5py.File('../we/west.h5', 'r')
we_iter = h5we['iterations']

# Potential 
rpot = np.linspace(0.5, 2.5, 200)
pot = V(rpot)

# set up figure and animation
fig = plt.figure(figsize=(10,4))
ax_bf = fig.add_subplot(211, autoscale_on=False,
                     xlim=(0.5, 2.5), ylim=(0, 10))

ax_we = fig.add_subplot(212, autoscale_on=False,
                     xlim=(0.5, 2.5), ylim=(0, 10))

bf_pot, = ax_bf.plot([], [], '-', lw=2)
we_pot, = ax_we.plot([], [], '-', lw=2)
bf_particle, = ax_bf.plot([], [], 'bo', ms=10)
we_particles, = ax_we.plot([], [], 'bo', ms=5) 
time_text = ax_bf.text(0.2, 0.9, '', transform=ax_bf.transAxes)


def init():
    bf_particle.set_data([], [])
    bf_pot.set_data([], [])
    we_pot.set_data([], [])
    we_particles.set_data([], [])
    time_text.set_text('')

    return bf_particle, bf_pot, we_pot, time_text


def animate(i):
    global bf_traj, rpot, pot, we_iter, vert_offset

    bf_pot.set_data(rpot, pot)
    we_pot.set_data(rpot, pot)
    bf_particle.set_data(bf_traj[i,0], bf_traj[i,1])

    pcoords = we_iter['iter_{:08d}'.format(i+1)]['pcoord'][:,1,0]
    pcoords_vert = V(pcoords) + vert_offset
    we_particles.set_data(pcoords, pcoords_vert)
    time_text.set_text('step = %d' % i)

    return bf_particle, bf_pot, we_pot, time_text

ani = animation.FuncAnimation(fig, animate, frames=step_lim,
                              interval=50, init_func=init)

plt.show()

h5bf.close()
h5we.close()







