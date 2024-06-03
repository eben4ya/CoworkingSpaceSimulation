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

# Run simulation


def run_simulation(scenario: str, screen: pygame.Surface, font: pygame.font.Font) -> tuple:
    """Run the coworking space simulation and return average results.

    Args:
        scenario (str): The distribution scenario ('left', 'right', 'normal').
        screen (pygame.Surface): The Pygame screen object for visualization.
        font (pygame.font.Font): The Pygame font object for text rendering.

    Returns:
        tuple: Average served students, average unserved students, and coworking space object.
    """
    served_students = 0
    unserved_students = 0

    for sim in range(SIMULATIONS):
        env = simpy.Environment()
        coworking_space = CoworkingSpace(env)
        env.process(student_arrival(env, coworking_space, scenario))

        for i in range(ITERATIONS):
            env.run(until=i + 1)
            visualize_iteration(screen, font, coworking_space, sim, i, 5 + i)
            
            pygame.time.wait(200)  # Add 0.2 second delay for each iteration

        served_students += coworking_space.served_students
        unserved_students += coworking_space.unserved_students

    avg_served = served_students / SIMULATIONS
    avg_unserved = unserved_students / SIMULATIONS
    return avg_served, avg_unserved, coworking_space


    
# Visualization with Pygame
def draw_grid(screen: pygame.Surface, container: simpy.Container, x_offset: int, y_offset: int, rows: int, cols: int, cell_size: int):
    """Draw a grid representing the container's occupancy.

    Args:
        screen (pygame.Surface): The Pygame screen object for visualization.
        container (simpy.Container): The container object to visualize.
        x_offset (int): The x-offset of the grid.
        y_offset (int): The y-offset of the grid.
        rows (int): The number of rows in the grid.
        cols (int): The number of columns in the grid.
        cell_size (int): The size of each cell in the grid.
    """
    for i in range(rows):
        for j in range(cols):
            rect = pygame.Rect(x_offset + j * cell_size,
                               y_offset + i * cell_size, cell_size, cell_size)
            color = (0, 255, 0) if i * cols + \
                j < container.level else (30, 30, 30)
            pygame.draw.rect(screen, color, rect,
                             0 if color == (0, 255, 0) else 1)


def visualize_iteration(screen: pygame.Surface, font: pygame.font.Font, coworking_space: CoworkingSpace, sim: int, iteration: int, hour: int):
    """Visualize the current iteration of the simulation.

    Args:
        screen (pygame.Surface): The Pygame screen object for visualization.
        font (pygame.font.Font): The Pygame font object for text rendering.
        coworking_space (CoworkingSpace): The coworking space object.
        sim (int): The current simulation number.
        iteration (int): The current iteration number.
        hour (int): the current hour.
    """
    screen.fill((240, 240, 240))

    # Draw containers
    draw_grid(screen, coworking_space.container1, 100, 175, 5, 9, 20)
    draw_grid(screen, coworking_space.container2, 350, 175, 4, 5, 20)
    draw_grid(screen, coworking_space.container3, 520, 175, 2, 5, 20)

    # Display text
    text_title = font.render(
        f'Coworking Space DTETI Simulation', True, (30, 30, 30))
    text_container1 = font.render(
        f'Container1', True, (30, 30, 30))
    text_container2 = font.render(
        f'Container2', True, (30, 30, 30))
    text_container3 = font.render(
        f'Container3', True, (30, 30, 30))
    text_simulation = font.render(
        f'Simulation: {sim + 1}/{SIMULATIONS}', True, (30, 30, 30))
    text_iteration = font.render(
        f'Iteration: {iteration + 1}/{ITERATIONS}', True, (30, 30, 30))
    text_hours = font.render(
        f'Hours: {hour + 1}.00', True, (30, 30, 30))
    text_arrive = font.render(
        f'arrival: {coworking_space.arrivals}', True, (30, 30, 30)
    )
    text_stay = font.render(
        f'duration: {coworking_space.stay_durations} hours', True, (30, 30, 30)
    )
    text_depart = font.render(
        f'depart: {coworking_space.departures}', True, (30, 30, 30)
    )
    text_served = font.render(
        f'Served: {coworking_space.served_students}', True, (0, 128, 0))
    text_unserved = font.render(
        f'Unserved: {coworking_space.unserved_students}', True, (255, 0, 0))

    screen.blit(text_title, (175, 50))
    screen.blit(text_container1, (100, 125))
    screen.blit(text_container2, (325, 125))
    screen.blit(text_container3, (520, 125))
    screen.blit(text_simulation, (75, 350))
    screen.blit(text_iteration, (75, 400))
    screen.blit(text_hours, (315, 350))
    screen.blit(text_arrive, (315, 400))
    screen.blit(text_stay, (315, 450))
    screen.blit(text_depart, (315, 500))
    screen.blit(text_served, (525, 350))
    screen.blit(text_unserved, (525, 400))

    pygame.display.flip()

def visualize_results(avg_served: float, avg_unserved: float, coworking_space: CoworkingSpace):
    """Visualize the results of the simulation.

    Args:
        avg_served (float): Average number of served students.
        avg_unserved (float): Average number of unserved students.
        coworking_space (CoworkingSpace): The coworking space object.
    """
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Coworking Space Simulation')
    # font = pygame.font.Font(None, 36)
    font = pygame.font.Font(None, 36)

    avg_text = font.render(
        f'Avg Served: {avg_served:.2f}, Avg Unserved: {avg_unserved:.2f}', True, (255, 255, 255))
    screen.blit(avg_text, (100, 50))
    pygame.display.flip()

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(60)

    pygame.quit()