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
    return np.abs(np.random.normal(10, 4))  # mean=10, std=4

# Modify the student_arrival function to update stays each iteration
def student_arrival(env: simpy.Environment, coworking_space: CoworkingSpace, scenario: str):
    """Simulate student arrivals based on the given scenario.

    Args:
        env (simpy.Environment): The simulation environment.
        coworking_space (CoworkingSpace): The coworking space object.
        scenario (str): The distribution scenario ('rarely', 'normal', 'capstone').
    """
    while True:
        if scenario == 'capstone':
            num_students = int(skewed_left())
            stay_duration = [int(np.random.beta(5, 2) * 7 + 1)
                             for _ in range(num_students)]
        elif scenario == 'rarely':
            num_students = int(skewed_right())
            stay_duration = [int(np.random.beta(2, 5) * 7 + 1)
                             for _ in range(num_students)]
        else:
            num_students = int(normal_distribution())
            stay_duration = [int(np.abs(np.random.normal(4)))
                             for _ in range(num_students)]

        if num_students > 0:
            env.process(coworking_space.process_students(
                num_students, stay_duration))

        yield env.timeout(1)
        env.process(coworking_space.update_stays())

    



