from common import Simulator


class Simple(Simulator):
    def calculate_distances(self):
        current_distance = self.get_distance(self.position)
        self.set_distance(self.position, current_distance + 1)


simulator = Simple(16, goals=[(7, 7), (7, 8), (8, 7), (8, 8)])
simulator.run()
