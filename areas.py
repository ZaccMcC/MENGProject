import numpy as np

class Areas:
    def __init__(self, title, position, direction, width, length):

        self.title = title
        self.position = np.array(position)
        self.direction = np.array(direction)

        self.width = width
        self.length = length

        self.corners = np.array([
            [self.position[0] - (self.width/2), self.position[1] + self.length/2], #Top left
            [self.position[0] + (self.width/2), self.position[1] + self.length/2], #Top right
            [self.position[0] + (self.width/2), self.position[1] - self.length/2], #Bottom right
            [self.position[0] - (self.width/2), self.position[1] - self.length/2]  #Bottom left
        ])

    def record_result(self, cords):
        print("Intersection coordinate at " + str(cords))
        print("At x = " + str(cords[0]) + " y = " + str(cords[1]) + " z = " + str(cords[2]))

        if self.corners[0][0] <= cords[0] <= self.corners[0][1]:
            print(str(cords[0]) + " is within the boundary " + str(self.corners[0][0]) + " : " + str(self.corners[0][1]))

        else:
            print(str(cords[0]) + " is NOT within the boundary " + str(self.corners[0][0]) + " : " + str(self.corners[0][1]))
