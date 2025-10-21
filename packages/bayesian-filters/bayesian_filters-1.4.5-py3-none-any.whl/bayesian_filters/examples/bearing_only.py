# -*- coding: utf-8 -*-
"""Copyright 2015 Roger R Labbe Jr.

FilterPy library.
https://github.com/GeorgePearse/bayesian_filters

Documentation at:
https://georgepearse.github.io/bayesian_filters

Supporting book at:
https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python

This is licensed under an MIT license. See the readme.MD file
for more information.
"""
# pylint: skip-file

import math
from numpy import array, asarray
from numpy.random import randn
import matplotlib.pyplot as plt

from bayesian_filters.kalman import UnscentedKalmanFilter as UKF
from bayesian_filters.kalman import ScaledUnscentedKalmanFilter as SUKF
from bayesian_filters.common import Q_discrete_white_noise


""" This is an example of the bearing only problem. You have a platform,
usually a ship, that can only get the bearing to a moving target. Assuming
platform is stationary, this is a very difficult problem because there are
an infinite number of solutions. The literature is filled with this example,
along with proposed solutions (usually, platform makes manuevers).

This is very old code; it no longer runs due to changes in the UKF
"""


dt = 0.1
y = 20
platform_pos = (0, 20)


sf = SUKF(2, 1, dt, alpha=1.0e-4, beta=2.0, kappa=1.0)
sf.Q = Q_discrete_white_noise(2, dt, 0.1)


f = UKF(2, 1, dt, kappa=0.0)
f.Q = Q_discrete_white_noise(2, dt, 0.1)


def fx(x, dt):
    """state transition function"""

    # pos = pos + vel
    # vel = vel
    return array([x[0] + x[1], x[1]])


def hx(x):
    """measurement function - convert position to bearing"""

    return math.atan2(platform_pos[1], x[0] - platform_pos[0])


xs_scaled = []
xs = []
for i in range(300):
    angle = hx([i + randn() * 0.1, 0]) + randn()
    sf.update(angle, hx, fx)
    xs_scaled.append(sf.x)

    f.predict(fx)
    f.update(angle, hx)
    xs.append(f.x)


xs_scaled = asarray(xs_scaled)
xs = asarray(xs)

plt.subplot(211)
plt.plot(xs_scaled[:, 0], label="scaled")
plt.plot(xs[:, 0], label="Julier")
plt.legend(loc=4)

plt.subplot(212)
plt.plot(xs_scaled[:, 1], label="scaled")
plt.plot(xs[:, 1], label="Julier")
plt.legend(loc=4)
plt.show()
