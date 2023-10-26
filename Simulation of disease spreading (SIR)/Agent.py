import numpy as np


class Agent:
    def __init__(self, x, y, lattice, beta, gamma, d, status):
        self.x = x
        self.y = y
        self.x_max = lattice[0]
        self.y_max = lattice[1]
        self.infection_rate = beta
        self.recovery_rate = gamma
        self.diffusion_rate = d
        self.status = status

    def move(self):
        if np.random.rand() < self.diffusion_rate:    # Move with p = diffusion_rate
            orientation = np.random.randint(4)
            if orientation == 0:
                self.x = min(self.x_max, self.x + 1)
            elif orientation == 1:
                self.x = max(0, self.x - 1)
            elif orientation == 2:
                self.y = min(self.y_max, self.y + 1)
            else:
                self.y = max(0, self.y - 1)

    def update_status(self, status):
        self.status = status
