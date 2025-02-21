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
## Checking for intersection between area and intersection (with sensor plane) coordinates
    def record_result(self, cords):
        #print("Intersection coordinate at " + str(cords))
        #print("At x = " + str(cords[0]) + " y = " + str(cords[1]) + " z = " + str(cords[2]))

        # # True, if intersection x coordinate is within area boundary
        # if self.corners[0][0] <= cords[0] <= self.corners[0][1]: #
        #     print(str(cords[0]) + " is within the boundary " + str(self.corners[0][0]) + " : " + str(self.corners[0][1]))
        # else:
        #     print(str(cords[0]) + " is NOT within the boundary " + str(self.corners[0][0]) + " : " + str(self.corners[0][1]))

            # True, if intersection x coordinate is within area boundary (x min and x max)
        if (self.position[0] - (self.width/2) <= cords[0] <= self.position[0] + (self.width/2)
            and # True, if intersection y coordinate is within area boundary (y min and y max)
            self.position[1] - (self.length/2) <= cords[1] <= self.position[1] + (self.length/2)):
                return 1
            #print("x coordinate " + str(cords[0]) + " is within the boundary " + str(self.position[0] - (self.width/2)) + " : " + str(self.position[0] + (self.width/2)))
            #print("y coordinate " + str(cords[1]) + " is within the boundary " + str(self.position[0] - (self.length/2)) + " : " + str(self.position[0] + (self.length/2)))
        else:
            #print("x coordinate " + str(cords[0]) + " is NOT within the boundary " + str(self.position[0] - (self.width/2)) + " : " + str(self.position[0] + (self.width/2)))
            #print("y coordinate " + str(cords[1]) + " is NOT within the boundary " + str(self.position[0] - (self.length/2)) + " : " + str(self.position[0] + (self.length/2)))
                return 0