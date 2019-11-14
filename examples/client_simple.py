from common import Simulator


class Simple(Simulator):
    def calculate_distances(self):
        """
        Instead of distances, use a counter to store the number of times we
        pass through a cell.
        """
        current_distance = self.get_distance(self.position)
        self.set_distance(self.position, current_distance + 1)

    def best_step(self):
        """
        Take a step into the neighbor cell with the lowest distance to center.
        """
        allowed = self.allowed_steps()
        distances = [self.distance_after_step(step) for step in allowed]
        best = distances.index(min(distances))
        return allowed[best]


simulator = Simple(16, goals=[(7, 7), (7, 8), (8, 7), (8, 8)])
simulator.run()
