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
fig = initialise_3d_plot(sourcePlane)
fig = visualise_environment(fig, sourcePlane, "yellow")

# thetaD = 45
# theta = np.radians(thetaD)
#
# def do_rotation(degrees, axis):
#     theta = np.radians(degrees)
#     if axis == "x":
#         R = np.array([
#             [1, 0, 0],
#             [0, np.cos(theta), - np.sin(theta)],
#             [0, np.sin(theta), np.cos(theta)]
#         ])
#     elif axis == "y":
#         R = np.array([
#             [np.cos(theta), 0, np.sin(theta)],
#             [0, 1, 0],
#             [-np.sin(theta), 0, np.cos(theta)]
#         ])
#     elif axis == "z":
#         R = np.array([
#             [np.cos(theta), - np.sin(theta), 0],
#             [np.sin(theta), np.cos(theta), 0],
#             [0, 0, 1]
#         ])
#     else :
#         print("Invalid axis")
#         R = np.array([1,1,1])
#     return R

# # X-axis Rotation
# rotated_plane_x = Plane(f"Rotated {thetaD} degrees in x-axis",
#                         sourcePlane.position,
#                         sourcePlane.direction,
#                         sourcePlane.width,
#                         sourcePlane.length)
#
# rotated_plane_x.rotate_plane(do_rotation(45, "x"))
#
# fig = visualise_environment(fig, rotated_plane_x, "green")
# #
# # Y-axis Rotation
# rotated_plane_y = Plane(f"Rotated {thetaD} degrees in y-axis",
#                         sourcePlane.position,
#                         sourcePlane.direction,
#                         sourcePlane.width,
#                         sourcePlane.length)
# rotated_plane_y.rotate_plane(do_rotation(45, "y"))
# fig = visualise_environment(fig, rotated_plane_y, "blue")
#
# # Z-axis Rotation
# rotated_plane_z = Plane(f"Rotated {thetaD} degrees in z-axis",
#                         sourcePlane.position,
#                         sourcePlane.direction,
#                         sourcePlane.width,
#                         sourcePlane.length)
# rotated_plane_z.rotate_plane(do_rotation(45, "z"))
# fig = visualise_environment(fig, rotated_plane_z, "purple")

# translated_plane = Plane(f"Translated {thetaD} degrees in z-axis",
#                                 sourcePlane.position,
#                                 sourcePlane.direction,
#                                 sourcePlane.width,
#                                 sourcePlane.length)
# translated_plane.translate_plane(np.array([0, 5, 0]))
# translated_plane.rotate_plane(do_rotation(thetaD, "z"))
