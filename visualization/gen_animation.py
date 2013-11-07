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

# Potential 
rpot = np.linspace(0.5, 2.5, 200)
pot = V(rpot)

# set up figure and animation
fig = plt.figure(figsize=(10,4))
ax = fig.add_subplot(111, autoscale_on=False,
                     xlim=(0.5, 2.5), ylim=(0, 10))
line, = ax.plot([], [], '-', lw=2)
particle, = ax.plot([], [], 'bo', ms=10)
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)


def init():
    particle.set_data([], [])
    line.set_data([], [])
    time_text.set_text('')

    return particle, line, time_text


def animate(i):
    global bf_traj, rpot, pot

    line.set_data(rpot, pot)
    particle.set_data(bf_traj[i,0], bf_traj[i,1])
    time_text.set_text('step = %d' % i)

    return particle, line, time_text

ani = animation.FuncAnimation(fig, animate, frames=step_lim,
                              interval=50, init_func=init)

plt.show()








