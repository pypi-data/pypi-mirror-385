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

from __future__ import absolute_import, division, print_function, unicode_literals

import numpy.random as random
import numpy as np
import matplotlib.pyplot as plt

from bayesian_filters.common import Saver
from bayesian_filters.kalman import KalmanFilter, InformationFilter


DO_PLOT = False


def test_1d_0P():
    global inf
    f = KalmanFilter(dim_x=2, dim_z=1)
    inf = InformationFilter(dim_x=2, dim_z=1)

    f.x = np.array([[2.0], [0.0]])  # initial state (location and velocity)

    f.F = np.array([[1.0, 1.0], [0.0, 1.0]])  # state transition matrix

    f.H = np.array([[1.0, 0.0]])  # Measurement function
    f.R = np.array([[5.0]])  # state uncertainty
    f.Q = np.eye(2) * 0.0001  # process uncertainty
    f.P = np.diag([20.0, 20.0])

    inf.x = f.x.copy()
    inf.F = f.F.copy()
    inf.H = np.array([[1.0, 0.0]])  # Measurement function
    inf.R_inv *= 1.0 / 5  # state uncertainty
    inf.Q = np.eye(2) * 0.0001
    inf.P_inv = 0.000000000000000000001
    # inf.P_inv = inv(f.P)

    m = []
    r = []
    r2 = []

    zs = []
    for t in range(50):
        # create measurement = t plus white noise
        z = t + random.randn() * np.sqrt(5)
        zs.append(z)

        # perform kalman filtering
        f.predict()
        f.update(z)

        inf.predict()
        inf.update(z)

        try:
            print(t, inf.P)
        except:
            pass

        # save data
        r.append(f.x[0, 0])
        r2.append(inf.x[0, 0])
        m.append(z)

    # assert np.allclose(f.x, inf.x), f'{t}: {f.x.T} {inf.x.T}'

    if DO_PLOT:
        plt.plot(m)
        plt.plot(r)
        plt.plot(r2)


def test_1d():
    global inf
    f = KalmanFilter(dim_x=2, dim_z=1)
    inf = InformationFilter(dim_x=2, dim_z=1)

    # ensure __repr__ doesn't assert
    str(inf)

    f.x = np.array([[2.0], [0.0]])  # initial state (location and velocity)

    inf.x = f.x.copy()
    f.F = np.array([[1.0, 1.0], [0.0, 1.0]])  # state transition matrix

    inf.F = f.F.copy()
    f.H = np.array([[1.0, 0.0]])  # Measurement function
    inf.H = np.array([[1.0, 0.0]])  # Measurement function
    f.R *= 5  # state uncertainty
    inf.R_inv *= 1.0 / 5  # state uncertainty
    f.Q *= 0.0001  # process uncertainty
    inf.Q *= 0.0001

    m = []
    r = []
    r2 = []
    zs = []
    s = Saver(inf)
    for t in range(100):
        # create measurement = t plus white noise
        z = t + random.randn() * 20
        zs.append(z)

        # perform kalman filtering
        f.update(z)
        f.predict()

        inf.update(z)
        inf.predict()

        # save data
        r.append(f.x[0, 0])
        r2.append(inf.x[0, 0])
        m.append(z)
        print(inf.y)
        s.save()

        assert abs(f.x[0, 0] - inf.x[0, 0]) < 1.0e-12

    if DO_PLOT:
        plt.plot(m)
        plt.plot(r)
        plt.plot(r2)


def test_against_kf():
    inv = np.linalg.inv

    dt = 1.0
    IM = np.eye(2)
    Q = np.array([[0.25, 0.5], [0.5, 1]])

    F = np.array([[1, dt], [0, 1]])
    # QI = inv(Q)
    inv(IM)

    from bayesian_filters.kalman import InformationFilter

    # f = IF2(2, 1)
    r_std = 0.2
    R = np.array([[r_std * r_std]])
    RI = inv(R)

    """f.F = F.copy()
    f.H = np.array([[1, 0.]])
    f.RI = RI.copy()
    f.Q = Q.copy()
    f.IM = IM.copy()"""

    kf = KalmanFilter(2, 1)
    kf.F = F.copy()
    kf.H = np.array([[1, 0.0]])
    kf.R = R.copy()
    kf.Q = Q.copy()

    f0 = InformationFilter(2, 1)
    f0.F = F.copy()
    f0.H = np.array([[1, 0.0]])
    f0.R_inv = RI.copy()
    f0.Q = Q.copy()

    # f.IM = np.zeros((2,2))

    for i in range(1, 50):
        z = i + (np.random.rand() * r_std)
        f0.predict()
        # f.predict()
        kf.predict()

        f0.update(z)
        # f.update(z)
        kf.update(z)

        print(f0.x.T, kf.x.T)
        assert np.allclose(f0.x, kf.x)
        # assert np.allclose(f.x, kf.x)


if __name__ == "__main__":
    DO_PLOT = True
    # test_1d_0P()
    test_1d()
    test_against_kf()
