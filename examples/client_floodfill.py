from itertools import product
from queue import Queue

from numpy import inf

from common import Simulator
from common import DIRECTIONS


class FloodFill(Simulator):
    def calculate_distances(self):
        queue = Queue()

        # Distances initialization
        for cell in product(range(self.size), range(self.size)):
            self.set_distance(cell, inf)
        for cell in self.goals:
            queue.put(cell)
            self.set_distance(cell, 0)

        # Flood fill
        while not queue.empty():
            cell = queue.get()
            distance = self.get_distance(cell) + 1
            for direction in DIRECTIONS:
                if self.has_wall(cell, direction):
                    continue
                neighbor = self.neighbor(cell, direction)
                if self.get_distance(neighbor) <= distance:
                    continue
                self.set_distance(neighbor, distance)
                queue.put(neighbor)


simulator = FloodFill(16, goals=[(7, 7), (7, 8), (8, 7), (8, 8)])
simulator.run()
