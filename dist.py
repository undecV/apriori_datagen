# -*- coding: UTF-8 -*-

import numpy as np


# TODO: todo...


def uniform_dist(low = 0.0, high = 1.0, size = None):
    return np.random.uniform(low, high, size)


def poisson_dist(lam = 1.0, size = None):
    return np.random.poisson(lam, size)


def normal_dist(loc = 0.0, scale = 1.0, size = None):
    return np.random.normal(loc, scale, size)


def exp_dist(scale = 1.0, size = None):
    return np.random.exponential(scale, size)


def choose():
    pass
