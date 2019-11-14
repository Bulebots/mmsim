from common import Simulator


class LeftWall(Simulator):
    def calculate_distances(self):
        """
        Distances are not recalculated, since they are not used.
        """
        pass

    def best_step(self):
        """
        Steps are taken based on a well-known preference.
        """
        allowed = self.allowed_steps()
        for step in ['left', 'front', 'right', 'back']:
            if step in allowed:
                return step


simulator = LeftWall(16, goals=[(7, 7), (7, 8), (8, 7), (8, 8)])
simulator.run()
