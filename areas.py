import numpy as np

import plotly.graph_objects as go


class Areas:
    def __init__(self, title, position, direction, width, length):

        self.title = title
        self.position = np.array(position)
        self.direction = np.array(direction)

        self.width = width
        self.length = length

        self.corners = np.array([
            [self.position[0] - (self.width / 2), self.position[1] + self.length / 2],  # Top left
            [self.position[0] + (self.width / 2), self.position[1] + self.length / 2],  # Top right
            [self.position[0] + (self.width / 2), self.position[1] - self.length / 2],  # Bottom right
            [self.position[0] - (self.width / 2), self.position[1] - self.length / 2]  # Bottom left
        ])

    ## Checking for intersection between area and intersection (with sensor plane) coordinates
    def record_result(self, cords):
        # True, if intersection x coordinate is within area boundary (x min and x max)
        if (self.position[0] - (self.width / 2) <= cords[0] <= self.position[0] + (self.width / 2)
                and  # True, if intersection y coordinate is within area boundary (y min and y max)
                self.position[1] - (self.length / 2) <= cords[1] <= self.position[1] + (self.length / 2)):
            return 1
        # print("x coordinate " + str(cords[0]) + " is within the boundary " + str(self.position[0] - (self.width/2)) + " : " + str(self.position[0] + (self.width/2)))
        # print("y coordinate " + str(cords[1]) + " is within the boundary " + str(self.position[0] - (self.length/2)) + " : " + str(self.position[0] + (self.length/2)))
        else:
            # print("x coordinate " + str(cords[0]) + " is NOT within the boundary " + str(self.position[0] - (self.width/2)) + " : " + str(self.position[0] + (self.width/2)))
            # print("y coordinate " + str(cords[1]) + " is NOT within the boundary " + str(self.position[0] - (self.length/2)) + " : " + str(self.position[0] + (self.length/2)))
            return 0

    def area_plot_3d(self, fig, colour):
        """Takes the geometry of the planes and prepared them for plotting on the input figure in the chosen colour"""
        x = np.linspace(-self.width / 2, self.width / 2, 50)
        y = np.linspace(-self.length / 2, self.length / 2, 50)
        x, y = np.meshgrid(x, y)

        z = np.ones_like(x) * int(self.position[2])  # Plane at z = 0 (sensor)

        # Define a uniform color (e.g., red)
        color_value = np.ones_like(z)

        fig.add_trace(go.Surface(z=z, x=x, y=y,
                                 # Ensures a uniform color
                                 surfacecolor=color_value,
                                 colorscale=[[0, colour], [1, colour]],  # Uniform red color
                                 showscale=False))  # Hide color scale

        return fig
