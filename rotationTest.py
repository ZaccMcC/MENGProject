from intersectionCalculations import intersection_wrapper  # Import for calculating line-plane intersection
from line import Line  # Import for Line object
from main import initialise_planes_and_areas, initialise_3d_plot, visualise_environment
from plane import Plane  # Import for Plane object
from areas import Areas  # Import for target areas
import numpy as np  # For mathematical operations
import plotly.graph_objects as go  # For 3D visualization


# Step 1: Initialize planes and areas
# sensorPlane, sourcePlane, interPlane, sensorArea = initialise_planes_and_areas()

# Step 2: Create 3D plot and visualize environment
fig = initialise_3d_plot()
# fig = visualise_environment(fig, sensorPlane, "red")
# fig = visualise_environment(fig, sourcePlane, "yellow")


def do_rotation():
    x = 1

# fig.show()

thetaD = 45
theta = np.radians(thetaD)
coords = np.array([0, 0, 1])
# R_x = np.array([[np.cos(theta), - np.sin(theta)],
#                 [np.sin(theta), np.cos(theta)]])

R_x = np.array([
                [1, 0, 0],
                [0, np.cos(theta), - np.sin(theta)],
                [0, np.sin(theta), np.cos(theta)]
                ])

R_y = np.array([
               [np.cos(theta), 0, np.sin(theta)],
               [0, 1, 0],
               [-np.sin(theta), 0, np.cos(theta)]
               ])

R_z = np.array([
                [np.cos(theta), - np.sin(theta), 0],
                [np.sin(theta), 0, np.cos(theta)],
                [0, 0, 1]
               ])


def rotate_coords(coords, R, colour):
    new_coords = np.dot(R, coords)

    direction = np.array([0, 0, 1])
    line1 = Line((coords[0], coords[1], coords[2]), direction)

    line1.plot_lines_3d(fig, [0,0,0], "green")

    line2 = Line((new_coords[0], new_coords[1], new_coords[2]), direction)

    line2.plot_lines_3d(fig, [0,0,0], colour)


    print("Coords are : ")
    print(coords)

    print("Rotation matrix is : ")
    print(R_x)

    print("New coords are: ")
    print(new_coords)

rotate_coords(coords, R_x, "blue")
rotate_coords(coords, R_y, "red")
rotate_coords(coords, R_z, "yellow")
fig.show()
