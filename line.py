import numpy as np

class Line:
    def __init__(self, position, direction):
        self.position = np.array(position)
        self.direction = np.array(direction)

