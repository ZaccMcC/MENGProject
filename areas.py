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

        # # Add labels at the corner points
        # for i, (xi, yi, zi) in enumerate(self.corners):
        #     fig.add_trace(go.Scatter3d(
        #         x=[xi], y=[yi], z=[zi],
        #         mode='text',
        #         text=f'P{i}',  # Label each corner as P0, P1, P2, etc.
        #         textposition='top center',
        #         showlegend=False,
        #         name = f"{self.title} (corner {i})"
        #     ))


        return fig