from intersectionCalculations import intersection_wrapper  # Import for calculating line-plane intersection
from line import Line  # Import for Line object
from main import initialise_planes_and_areas, initialise_3d_plot, visualise_environment
from plane import Plane  # Import for Plane object
from areas import Areas  # Import for target areas
import numpy as np  # For mathematical operations
import plotly.graph_objects as go  # For 3D visualization


# Step 1: Initialize planes and areas
sensorPlane, sourcePlane, interPlane, sensorArea = initialise_planes_and_areas()

# Step 2: Create 3D plot and visualize environment
fig = initialise_3d_plot()
fig = visualise_environment(fig, sensorPlane, "red")
fig = visualise_environment(fig, sourcePlane, "yellow")


def do_rotation():
    x = 1

# fig.show()

thetaD = 45
theta = np.radians(thetaD)
coords = np.array([4,1])
R_x = np.array([[np.cos(theta), - np.sin(theta)], [np.sin(theta), np.cos(theta)]])

new_coords = np.dot(R_x, coords)

print("Coords are : ")
print(coords)

print("Rotation matrix is : ")
print(R_x)

print("New coords are: ")
print(new_coords)

