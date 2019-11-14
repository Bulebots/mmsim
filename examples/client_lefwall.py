from common import Simulator


class LeftWall(Simulator):
    def calculate_distances(self):
        pass

    def best_step(self):
        allowed = self.allowed_steps()
        for step in ['left', 'front', 'right', 'back']:
            if step in allowed:
                return step


simulator = LeftWall(16, goals=[(7, 7), (7, 8), (8, 7), (8, 8)])
simulator.run()
