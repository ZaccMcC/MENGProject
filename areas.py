import numpy as np


from plane import compute_local_axes


class Areas:
    def __init__(self, title, position, direction, width, length):

        self.corners = None
        self.title = title
        self.position = np.array(position)
        self.direction = np.array(direction)

        self.width = width
        self.length = length

        # Compute local reference frame (right, up, normal)
        self.right, self.up, self.normal = compute_local_axes(self.direction)

        # Stores the 'illumination' results
        self.illumination = None

        # Compute initial corners using the local frame
        self.update_corners()

        # print(self.corners)

    def update_corners(self):
        """
        Recalculate the area's corner positions using its local coordinate system.
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


    ## Checking for intersection between area and intersection (with sensor plane) coordinates
    def record_result(self, cords):
        # True, if intersection x coordinate is within area boundary (x min and x max)
        if (self.position[0] - (self.width / 2) <= cords[0] <= self.position[0] + (self.width / 2)
                and  # True, if intersection y coordinate is within area boundary (y min and y max)
                self.position[1] - (self.length / 2) <= cords[1] <= self.position[1] + (self.length / 2)):
            return 1
        else:
            return 0

    # def planes_plot_3d(self, fig, colour):
    #     """Takes the geometry of the planes and prepared them for plotting on the input figure in the chosen colour"""
    #     x = np.linspace(-self.width / 2, self.width / 2, 50)
    #     y = np.linspace(-self.length / 2, self.length / 2, 50)
    #     x, y = np.meshgrid(x, y)
    #
    #     z = np.ones_like(x) * int(self.position[2])  # Plane at z = 0 (sensor)
    #
    #     # Define a uniform color (e.g., red)
    #     color_value = np.ones_like(z)
    #
    #     fig.add_trace(go.Surface(z=z, x=x, y=y,
    #                              # Ensures a uniform color
    #                              surfacecolor=color_value,
    #                              colorscale=[[0, colour], [1, colour]],  # Uniform red color
    #                              showscale=False))  # Hide color scale
    #
    #     return fig

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
                showlegend=False,
                name = f"{self.title} (corner {i})"
            ))

        local_axis = np.array([self.right, self.up, self.normal])
        local_axis_colours = ['red', 'green', 'blue']
        local_axis_names = ['Right', 'Up', 'Normal']

        # for i in range(3):
        #     unit_vector = local_axis[i] / np.linalg.norm(local_axis[i])  # Normalize
        #     start = self.position  # Origin of local axes at plane's position
        #     end = self.position + unit_vector  # Unit length
        #
        #     fig.add_trace(go.Scatter3d(
        #         x=[start[0], end[0]],
        #         y=[start[1], end[1]],
        #         z=[start[2], end[2]],
        #         mode='lines+markers',
        #         line=dict(color=local_axis_colours[i], width=5),
        #         marker=dict(size=8, color=local_axis_colours[i], opacity=0.8),
        #         name=local_axis_names[i],
        #         showlegend=False
        #     ))


        return fig