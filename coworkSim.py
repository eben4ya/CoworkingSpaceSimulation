# import modul
import simpy
import random
import numpy as np
import pygame

# Define constants
CAPACITY1 = 45
CAPACITY2 = 20
CAPACITY3 = 10
ITERATIONS = 17  # 06.00 - 22.00
SIMULATIONS = 15

# Define distributions for scenarios


def skewed_left() -> float:
    """Generate a random number with a left-skewed distribution."""
    return np.random.beta(5, 2) * 20


def skewed_right() -> float:
    """Generate a random number with a right-skewed distribution."""
    return np.random.beta(2, 5) * 20


def normal_distribution() -> float:
    """Generate a random number with a normal distribution."""
    return np.abs(np.random.normal(10, 4)) # mean=10, std=4

