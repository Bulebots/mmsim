"""
Common code shared among different simulators/solvers.
"""
import struct
from abc import ABCMeta
from abc import abstractmethod
from collections import deque
from itertools import product

import zmq


def _map_rotated_list(lst, rotation):
    q = deque(lst)
    q.rotate(rotation)
    return dict(zip(lst, q))


STEPS = ('front', 'left', 'right', 'back')
DIRECTIONS = ('north', 'east', 'south', 'west')
DIRECTION_AFTER_STEP = dict(
    zip(
        ('front', 'left', 'back', 'right'),
        (_map_rotated_list(DIRECTIONS, rotation) for rotation in range(4)),
    )
)
NEIGHBOR_POSITION_CHANGE = {
    'north': (0, 1),
    'east': (1, 0),
    'south': (0, -1),
    'west': (-1, 0),
}


class Client(metaclass=ABCMeta):
    """
    Basic interface to communicate with the simulation server.
    """
    def __init__(self):
        self.ctx = zmq.Context()
        self.req = self.ctx.socket(zmq.REQ)
        self.req.connect('tcp://127.0.0.1:6574')

    def reset(self):
        self.req.send(b'reset')
        return self.req.recv()

    def read_walls(self, maze):
        direction = maze.direction[0].upper().encode()
        self.req.send(b'W' + struct.pack('2B', *maze.position) + direction)
        return struct.unpack('3B', self.req.recv())

    def send_state(self, maze):
        direction = maze.direction[0].upper().encode()
        state = b'S' + struct.pack('2B', *maze.position) + direction
        state += b'F'
        for row in maze.distances:
            for distance in row:
                state += struct.pack('B', distance)
        state += b'F'
        for row in maze.walls:
            for walls in row:
                value = walls['visited']
                value += walls['east'] << 1
                value += walls['south'] << 2
                value += walls['west'] << 3
                value += walls['north'] << 4
                state += struct.pack('B', value)
        self.req.send(state)
        return self.req.recv()


class Simulator:
    """
    Create and update the world environment as seen by the robot.
    """
    def __init__(self, size, goals):
        self.size = size
        self.goals = goals
        self.walls = [[{} for y in range(size)] for x in range(size)]
        self.distances = [[0 for y in range(size)] for x in range(size)]
        self.position = (0, 0)
        self.direction = 'north'
        self.reset_walls()
        self.calculate_distances()

    def reset_walls(self):
        for x, y in product(range(self.size), range(self.size)):
            self.walls[x][y] = {
                'east': 0,
                'south': 0,
                'west': 0,
                'north': 0,
                'visited': 0,
            }
        for i in range(self.size):
            self.walls[0][i]['west'] = 1
            self.walls[i][0]['south'] = 1
            self.walls[self.size - 1][i]['east'] = 1
            self.walls[i][self.size - 1]['north'] = 1

    def get_distance(self, cell):
        return self.distances[cell[0]][cell[1]]

    def set_distance(self, cell, value):
        self.distances[cell[0]][cell[1]] = value

    def has_wall(self, cell, direction):
        x, y = cell
        return bool(self.walls[x][y][direction])

    def neighbor(self, cell, direction):
        x, y = cell
        dx, dy = NEIGHBOR_POSITION_CHANGE[direction]
        return (x + dx, y + dy)

    def _build_neighbor_wall(self, direction, wall):
        x, y = self.neighbor(self.position, direction)
        direction = DIRECTION_AFTER_STEP['back'][direction]
        self.walls[x][y][direction] = wall

    def _build_walls(self, walls):
        x, y = self.position
        for direction, wall in walls.items():
            if not wall:
                continue
            if self.walls[x][y][direction] == wall:
                continue
            self.walls[x][y][direction] = wall
            self._build_neighbor_wall(direction, wall)
        self.walls[x][y]['visited'] = 1

    def update_walls(self, left, front, right):
        rotations = {'east': 0, 'south': 1, 'west': 2, 'north': 3}
        walls = deque([left, front, right, 0])
        walls.rotate(rotations[self.direction])
        walls = dict(zip(DIRECTIONS, walls))
        self._build_walls(walls)

    def position_after_step(self, step):
        direction = DIRECTION_AFTER_STEP[step][self.direction]
        return self.neighbor(self.position, direction)

    def move(self, step):
        self.position = self.position_after_step(step)
        self.direction = DIRECTION_AFTER_STEP[step][self.direction]

    def _is_allowed_step(self, step):
        x, y = self.position
        direction = DIRECTION_AFTER_STEP[step][self.direction]
        return not self.walls[x][y][direction]

    def allowed_steps(self):
        return [step for step in STEPS if self._is_allowed_step(step)]

    def distance_after_step(self, step):
        position = self.position_after_step(step)
        return self.get_distance(position)

    def run(self):
        client = Client()
        client.reset()
        for _ in range(1000):
            self.update_walls(*client.read_walls(self))
            self.calculate_distances()
            client.send_state(self)
            if self.position in self.goals:
                break
            self.move(self.best_step())

    @abstractmethod
    def calculate_distances(self):
        raise NotImplementedError

    @abstractmethod
    def best_step(self):
        raise NotImplementedError
