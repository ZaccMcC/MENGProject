import plotly.graph_objects as go
import numpy as np

def planes_plot(fig, graphicPlane, colour):
    x = np.linspace(-graphicPlane.width/2, graphicPlane.width/2, 50)
    y = np.linspace(-graphicPlane.length/2, graphicPlane.length/2, 50)
    x, y = np.meshgrid(x, y)

    z = np.ones_like(x) * int(graphicPlane.position[2])  # Plane at z = 0 (sensor)

    # Define a uniform color (e.g., red)
    color_value = np.ones_like(z)  # Needed for `surfacecolor`


    fig.add_trace(go.Surface(z=z, x=x, y=y,
    # Ensures a uniform color
    surfacecolor=color_value,
    colorscale=[[0, colour], [1, colour]],  # Uniform red color
    showscale=False))  # Hide color scale

    return fig

def plot_lines(fig, line, cords, colour):

   # fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z =[1, 0], mode='lines'))

    #Add lines bounded by:
        # line.position = coordinates on source plane
        # cords = coordinates of intersection with sensor plane
    x = [line.position[0], cords[0]]
    y = [line.position[1], cords[1]]
    z = [line.position[2], cords[2]]
    fig.add_trace(go.Scatter3d(x=x, y=y, z =z, mode='lines',showlegend=False,line = {'color' : colour, 'width' : 3}))

    return fig