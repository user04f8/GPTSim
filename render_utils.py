import random
import math
from typing import Dict, Tuple, Set

from simulated.rooms import Environment

DISTANCE_POW = 1/2

SCALE = 1.0

def distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** (1/2) / SCALE

def reduce_overlap(d, d_max=150):
     return min(d, d_max) ** (1/3)

def connected_reward(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        d = distance(p1, p2)
        return 2*max(-300, min(d, 300-d)) + 100*reduce_overlap(d)

def reward(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        d = distance(p1, p2)
        return max(0, min(d, 900-d)) ** (1/2) + 100*reduce_overlap(d)


# def edge_penalty(p: Tuple[int, int], x_range: Tuple[int, int], y_range: Tuple[int, int]):
#     edge_size = min(x_range[1] - x_range[0], y_range[1] - y_range[0]) / 2
#     x, y = p
#     return - min(x - x_range[0], x_range[1] - x, y - y_range[0], y_range[1] - y, edge_size)

def calculate_objective(room_positions: Dict[str, Tuple[int, int]], environment: Environment) -> float:
    objective = 0.0
    rooms = list(environment.all_rooms_by_name.values())
    for i, room1 in enumerate(rooms):
        # objective += edge_penalty(room_positions[room1.name], x_range, y_range)
        for j, room2 in enumerate(rooms):
            if i < j:
                if room2 in room1.adjacent_rooms:
                    objective += connected_reward(room_positions[room1.name], room_positions[room2.name])
                else:
                    objective += reward(room_positions[room1.name], room_positions[room2.name])
    return objective

def simulated_annealing(environment: Environment, x_range: Tuple[int, int], y_range: Tuple[int, int], initial_temp: float, cooling_rate: float) -> Dict[str, Tuple[int, int]]:
    current_positions = {room.name: (random.randint(*x_range), random.randint(*y_range)) for room in environment.all_rooms_by_name.values()}
    current_objective = calculate_objective(current_positions, environment)
    temp = initial_temp

    while temp > 1:
        new_positions = current_positions.copy()
        room_to_move = random.choice(list(new_positions.keys()))
        new_positions[room_to_move] = (random.randint(*x_range), random.randint(*y_range))

        new_objective = calculate_objective(new_positions, environment)
        delta = new_objective - current_objective

        if delta > 0 or random.uniform(0, 1) < math.exp(delta / temp):
            current_positions = new_positions
            current_objective = new_objective

        temp *= cooling_rate

    return current_positions

def optimize_room_positions(environment: Environment, x_range: Tuple[int, int], y_range: Tuple[int, int]) -> Dict[str, Tuple[int, int]]:
    initial_temp = 100.0
    cooling_rate = 0.997
    n_tries = 5
    max_obj = None
    for i in range(n_tries):
        candidate_pos = simulated_annealing(environment, x_range, y_range, initial_temp, cooling_rate)
        obj = calculate_objective(candidate_pos, environment)
        #  print(obj)
        if max_obj is None or obj > max_obj:
            best_pos = candidate_pos
    return best_pos

# Example usage:
# environment = Environment(all_rooms)
# max_x, max_y = 100, 100
# alpha = 0.5
# optimized_positions = optimize_room_positions(environment, max_x, max_y, alpha)
# print(optimized_positions)
