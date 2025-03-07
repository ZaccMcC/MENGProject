import numpy as np
from matplotlib import pyplot as plt
import random

class Plane:
    """
    A class to represent a 3D plane with plotting and point generation methods.

    Attributes:
    title (str): The name of the plane.
    position (np.array): The position of the plane in 3D space.
    direction (np.array): The direction vector of the plane.
    width (float): The width of the plane.
    length (float): The length of the plane.
    corners (np.array): The 3D coordinates of the plane's corners.
    """

    def __init__(self, title, position, direction, width, length):
        """
    Initialize a Plane instance.

    Args:
        title (str): The name of the plane.
        position (list or array): The center position of the plane in 3D space [x, y, z].
        direction (list or array): The direction vector of the plane [e.g. normal vector].
        width (float): The width of the plane.
        length (float): The length of the plane.
    """

        self.corners = None
        self.title = title
        self.position = np.array(position)
        self.direction = np.array(direction)

        self.width = width
        self.length = length

        # Compute local reference frame (right, up, normal)
        self.right, self.up, self.direction = compute_local_axes(self.direction)

        # Compute initial corners using the local frame
        self.update_corners()

    def update_corners(self):
        """
        Recalculate the plane's corner positions using its local coordinate system.
        """
        half_width = self.width / 2
        half_length = self.length / 2
        # Compute corners relative to the center using the local basis vectors
        self.corners = np.array([
            self.position + (-half_width * self.right + half_length * self.up),  # Top Left
            self.position + (half_width * self.right + half_length * self.up),   # Top Right
            self.position + (half_width * self.right - half_length * self.up),   # Bottom Right
            self.position + (-half_width * self.right - half_length * self.up)   # Bottom Left
        ])

    def rotate_plane(self, rotation_matrix):
        """
        Rotates the plane by applying a rotation matrix to its local coordinate system.

        Args:
            rotation_matrix (np.array): 3x3 rotation matrix.
        """
        # print(f"Rotated --- right: {self.right}, up: {self.up}, normal: {self.normal}")
        # Rotate local axes
        self.right = np.dot(rotation_matrix, self.right)
        self.up = np.dot(rotation_matrix, self.up)
        self.direction = np.dot(rotation_matrix, self.direction)
        # print(f"Rotated --- right: {self.right}, up: {self.up}, normal: {self.normal}")
        # Recalculate corners after rotating the local frame
        self.update_corners()

    def translate_plane(self, translation_vector):
        self.position = self.position + translation_vector
        self.corners = self.corners + translation_vector
        self.update_corners()

    def planes_plot_3d(self, fig, colour):
        """
        Add a 3D representation of the plane to a Plotly figure.

        Args:
            fig (plotly.graph_objects.Figure): The figure object to which the plane will be added.
            colour (str): The color for the plane surface.

        Returns:
            plotly.graph_objects.Figure: Updated figure object.
        """
        from plotly import graph_objects as go

        # Extract corner coordinates
        x, y, z = zip(*self.corners)

        # Create a surface plot using the four corners
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            color=colour,
            opacity=0.5,
            name=self.title
        ))

            # Add a dummy trace for the legend
        fig.add_trace(go.Scatter3d(
            x=[x[0]], y=[y[0]], z=[z[0]],  # Single point (dummy)
            mode='markers',
            marker=dict(size=5, color=colour, opacity=0.5),
            name=self.title,  # Legend entry
            showlegend=True
        ))

        # Add labels at the corner points
        for i, (xi, yi, zi) in enumerate(self.corners):
            fig.add_trace(go.Scatter3d(
                x=[xi], y=[yi], z=[zi],
                mode='text',
                text=f'P{i}',  # Label each corner as P0, P1, P2, etc.
                textposition='top center',
                showlegend=False
            ))

        local_axis = np.array([self.right, self.up, self.direction])
        local_axis_colours = ['red', 'green', 'blue']
        local_axis_names = ['Right', 'Up', 'Normal']

        for i in range(3):
            unit_vector = local_axis[i] / np.linalg.norm(local_axis[i])  # Normalize
            start = self.position  # Origin of local axes at plane's position
            end = self.position + unit_vector  # Unit length

            fig.add_trace(go.Scatter3d(
                x=[start[0], end[0]],
                y=[start[1], end[1]],
                z=[start[2], end[2]],
                mode='lines+markers',
                line=dict(color=local_axis_colours[i], width=5),
                marker=dict(size=8, color=local_axis_colours[i], opacity=0.8),
                name=local_axis_names[i],
                showlegend=False
            ))


        return fig


    def plot_area(self):
        """
        Plot the 2D representation of the plane's area using matplotlib.
        """
        for i in range(len(self.corners)):
            # Plot the plane corners
            plt.plot(self.corners[i][0], self.corners[i][1], marker='*', color='green')

            # Connect consecutive corners to form edges
            if i < len(self.corners) - 1:
                x_positions = np.linspace(self.corners[i][0], self.corners[i + 1][0], 5)
                y_positions = np.linspace(self.corners[i][1], self.corners[i + 1][1], 5)
            else:  # Connect the last corner to the first corner
                x_positions = np.linspace(self.corners[i][0], self.corners[0][0], 5)
                y_positions = np.linspace(self.corners[i][1], self.corners[0][1], 5)

            plt.plot(x_positions, y_positions, color='green')  # Plot edge lines

        plt.title(f"Area of {self.title}")


    def random_points(self, quantity):
        """
        Generate random points within the plane boundaries.

        Args:
            quantity (int): The number of random points to generate.

        Returns:
            np.array: Array of random (x, y) points on the plane.
        """
        points = []  # Placeholder for the generated points

        for _ in range(quantity):
            # Generate random coordinates (x, y) within plane dimensions
            x = random.uniform(-self.width / 2, self.width / 2)
            y = random.uniform(-self.length / 2, self.length / 2)
            points.append([x, y])

        # Convert the list of points into a Numpy array
        return np.array(points)

    def plot_points(self, point):
        """
        Plot a single point on the 2D plane using matplotlib.

        Args:
            point (list or array): The (x, y) coordinates of the point to plot.
        """
        plt.plot(point[0], point[1], marker='*', color='red')

def compute_local_axes(normal):
    """
    Compute a local coordinate system (right, up, normal) based on a given normal vector.

    Args:
        normal (np.array): The plane's normal vector.

    Returns:
        right (np.array): Right vector (width direction).
        up (np.array): Up vector (length direction).
        normal (np.array): Normalized normal vector.
    """
    normal = normal / np.linalg.norm(normal)  # Ensure it's a unit vector

    # Choose an arbitrary world up vector (shouldn't be parallel to normal)
    world_up = np.array([0, 1, 0])

    # If normal is parallel to world_up, use a different reference
    if np.allclose(normal, world_up):
        world_up = np.array([1, 0, 0])

    # Compute right (cross product of world_up and normal)
    # print(f"World up: {world_up} dot normal: {(normal)}")
    right = np.cross(world_up, normal)
    # print(f"Right: {right}")
    right = right / np.linalg.norm(right)  # Normalize
    # print(f"Right: {right}")
    # Compute up (cross product of normal and right)
    up = np.cross(normal, right)

    # print(f"World up: {world_up} normal: {normal} and right {right} and up {up}")

    return right, up, normal  # Return orthonormal basis

