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

class CoworkingSpace:
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.container1 = simpy.Container(env, capacity=CAPACITY1, init=0)
        self.container2 = simpy.Container(env, capacity=CAPACITY2, init=0)
        self.container3 = simpy.Container(env, capacity=CAPACITY3, init=0)
        self.unserved_students = 0
        self.served_students = 0
        self.arrivals = 0
        self.departures = 0
        self.stay_durations = []
        self.stay_info = []  # New list to keep track of stay information

    def process_students(self, num_students: int, stay_durations: list):
        """Process student arrivals and departures in the coworking space.

        Args:
            num_students (int): Number of students arriving.
            stay_durations (int): Duration of stay for each student.
        """
        served = 0
        unserved = 0
        self.arrivals = num_students
        self.stay_durations = stay_durations

        containers = [self.container1, self.container2, self.container3]
        capacities = [CAPACITY1, CAPACITY2, CAPACITY3]

        # Student arrival
        for stay_duration in stay_durations:
            container_indices = list(range(len(containers)))
            random.shuffle(container_indices)
            placed = False

            for index in container_indices:
                if containers[index].level < capacities[index]:
                    yield containers[index].put(1)
                    served += 1
                    placed = True
                    self.stay_info.append((containers[index], stay_duration))
                    break

            if not placed:
                unserved += 1

        self.served_students += served
        self.unserved_students += unserved

    def update_stays(self):
        """Update the stay durations and process student departures."""
        self.stay_info = [(container, stay_duration - 1)
                          for container, stay_duration in self.stay_info]

        # Remove students whose stay duration is over
        self.departures = 0
        for container, stay_duration in self.stay_info:
            if stay_duration <= 0:
                yield container.get(1)
                self.departures += 1

        self.stay_info = [(container, stay_duration) for container,
                          stay_duration in self.stay_info if stay_duration > 0]
        



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

    



