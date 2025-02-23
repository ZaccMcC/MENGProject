import numpy as np
import plotly.graph_objects as go

class Line:
    def __init__(self, position, direction):
        self.position = np.array(position)
        self.direction = np.array(direction)

    def plot_lines_3d(self, fig, cords, colour):
        """Add lines bounded by:
            # line.position = coordinates on source plane
            # cords = coordinates of intersection with sensor plane """
        x = [self.position[0], cords[0]]
        y = [self.position[1], cords[1]]
        z = [self.position[2], cords[2]]
        fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', showlegend=False, line={'color': colour, 'width': 3}))

        return fig
