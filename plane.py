import numpy as np
from matplotlib import pyplot as plt
import random


class Plane:
    def __init__(self, title, position, direction, width, length):

        self.title = title
        self.position = np.array(position)
        self.direction = np.array(direction)

        self.width = width
        self.length = length

        self.corners = np.array([
                        [self.position[0] - (self.width/2), self.position[1] + self.length/2],
                        [self.position[0] + (self.width/2), self.position[1] + self.length/2],
                        [self.position[0] + (self.width/2), self.position[1] - self.length/2],
                        [self.position[0] - (self.width/2), self.position[1] - self.length/2]
        ])

    def plot_area(self):
        for i in range(0, len(self.corners)):
            plt.plot(self.corners[i][0], self.corners[i][1], marker = '*', color='green') # Plot corners

            if i < len(self.corners)-1: # Do until last corner
                plt.plot(
                np.linspace(self.corners[i][0], self.corners[i+1][0], 5), # Generate x positions between x_i and x_i+1
                np.linspace(self.corners[i][1], self.corners[i+1][1], 5), #Generate x positions between y_i and y_i+1
                color='green'
                )
            else: # For last corner, connect to first corner
                plt.plot(
                    np.linspace(self.corners[i][0], self.corners[0][0], 5), # Generate x positions between x_i and x_i+1
                    np.linspace(self.corners[i][1], self.corners[0][1], 5), #Generate x positions between y_i and y_i+1
                    color='green'
                )
            plt.title("Area of " + self.title)

    def random_points(self, quantity):
        # points = np.empty([quantity, 2]) # Pre-allocate array
        points = [] # Pre-allocate arra

        for i in range(0, quantity):
            # Generate random point
            x = random.uniform(-self.width/2, self.width/2)
            y = random.uniform(-self.length/2, self.length/2)

            #Store points in array
            points.append([x, y])

            # print(f"Random point: ({x}, {y})")

        points_array = np.array(points)
        return points_array

    def plot_points(self, point):
        plt.plot(point[0], point[1], marker = '*', color='red')
