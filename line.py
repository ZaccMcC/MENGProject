import logging

import numpy as np
import plotly.graph_objects as go

class Line:
    def __init__(self, local_position, direction):
        """
        Initializes a line with its position relative to a plane.

        Args:
            local_position (array): The position of the line in the plane's local coordinate system.
            direction (array): The initial direction (same as plane's normal).
        """
        self.local_position = np.array(local_position)  # Stored in local coordinates
        self.position = None  # Will be computed in global coordinates
        self.direction = np.array(direction)

    def plot_lines_3d(self, fig, intersection, color):
        """
        Adds the line to the 3D plot.

        Args:
            fig (Plotly figure): The figure to plot.
            intersection (array): The intersection point with the sensor plane.
            color (str): Line color.

        Returns:
            fig (Plotly figure): Updated figure.
        """
        x = [self.position[0], intersection[0]]
        y = [self.position[1], intersection[1]]
        z = [self.position[2], intersection[2]]

        fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', showlegend=False,
                                   line={'color': color, 'width': 3}))

        return fig

    def update_position(self, plane):
        """
        Updates the line's new position, after rotation of the plane

        :return: global coordinate of line starting point
        """
        self.position = plane.position + np.dot(self.local_position, np.vstack((plane.right, plane.up, plane.direction)))

        self.position = np.add(plane.position, np.add(self.position[0] * plane.right, self.position[1] * plane.up, self.position[2] * plane.direction))
        # self.direction = plane.direction
        # print(f"New position = {self.position}")

    def update_global_position(self, plane):
        """
        Updates the global position of the line based on the transformed plane.
        Args:
            plane (Plane): The updated plane after movement.
        """
        # logging.debug(f"Line has local position {self.local_position} and direction {self.direction}")
        # if self.position is None:
        #     logging.debug("Global position not defined yet.")
        # else:
        #     logging.debug(f"Current global position: {self.position}")

        self.position = plane.position + (self.local_position[0] * plane.right +
                                          self.local_position[1] * plane.up +
                                          self.local_position[2] * plane.direction)
        self.direction = plane.direction

        # logging.debug(f"New global position: {self.position}")