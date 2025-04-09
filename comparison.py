import json

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

def draw_rectangle(ax, centre, width, length, z, label, colour='green', alpha=0.5):
    x, y = centre
    # Define rectangle corners (assumes it's aligned with axes)
    corners = np.array([
        [x - width / 2, y - length / 2, z],
        [x + width / 2, y - length / 2, z],
        [x + width / 2, y + length / 2, z],
        [x - width / 2, y + length / 2, z]
    ])
    # Draw rectangle
    rect = Poly3DCollection([corners], facecolors=colour, alpha=alpha, edgecolors='k')
    ax.add_collection3d(rect)
    # Add label
    ax.text(x, y, z + 0.1, label, ha='center', va='bottom', fontsize=8)

def plot_areas_3d(config):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot sensor areas
    for sensor in config.get("sensor_areas", {}).values():
        x, y, z = sensor["position"]
        draw_rectangle(ax, (x, y), sensor["width"], sensor["length"], z,
                       sensor["title"], colour='green', alpha=0.6)

    # Plot aperture areas
    for aperture in config.get("aperture_areas", {}).values():
        x, y, z = aperture["position"]
        draw_rectangle(ax, (x, y), aperture["width"], aperture["length"], z,
                       aperture["title"], colour='gray', alpha=0.4)

    # Axes setup
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Sensor and Aperture Layout')

    ax.grid(True)
    ax.view_init(elev=20, azim=60)  # Adjust the viewing angle
    plt.tight_layout()
    plt.show()


with open("config.json") as f:
    config = json.load(f)

# plot_areas_3d(config)

