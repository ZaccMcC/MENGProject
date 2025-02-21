from graphicPlot import planes_plot, plot_lines
from intersectionCalculations import intersection_wrapper
from line import Line
from plane import Plane
from areas import Areas
import numpy as np
import plotly.graph_objects as go

import random
import matplotlib.pyplot as plt

##### Initial definitions

# Defines position and direction arrays for line
position = np.array([0,0,1])
direction = np.array([0,0,1])

# Create instance "line1" of object Line with pos and dir
line1 = Line(position, direction)

# Defines position and direction arrays for sensor plane
position = np.array([0,0,0])
direction = np.array([0,0,1])

# Defines source plane
sensorPlane = Plane("Sensor Plane",position, direction, 10, 10)

# Defines position and direction arrays for source plane
position = np.array([0,0,2])
direction = np.array([0,0,1])

# Defines source plane
sourcePlane = Plane("Source Plane", position, direction, 10, 10)

# Defines position and direction arrays for test plane
position = np.array([0,0,1])
direction = np.array([0,0,1])

# Defines test plane
interPlane = Plane("Interplane", position, direction, 5, 5)

# Define test area
position = np.array([0,0,0])
direction = np.array([0,0,1])
# areas(self, title, position, direction, width, length):
sensorArea = Areas("Sensor", position, direction, 1, 1)
# def direction_vectors(array1, array2):
#     check_direction = np.multiply(array1, array2)
#     check_direction = np.sum(check_direction)
#     return check_direction
#
#
# def parametric_equation(np, na, nu):
#     return (np - na)/nu
#
#
# def calculate_intersection(line, t):
#     x = line.direction[0] * t + line.position[0]
#     y = line.direction[1] * t + line.position[1]
#     z = line.direction[2] * t + line.position[2]
#
#     #coordinates = (x,y,z)
#     coordinates = np.array([x,y,z])
#     return coordinates
#
# nU = direction_vectors(sensorPlane.direction, line1.direction)
#
#
# if nU > 0:
#     #print(nU)
#     nA = direction_vectors(sensorPlane.direction, line1.position)
#     nP = direction_vectors(sensorPlane.direction, sensorPlane.position)
#
#     #print(nA)
#     #print(nP)
#     x = parametric_equation(nP, nA, nU)
#     IntersectionCoordinates = calculate_intersection(line1, x)
#     print("Intersection occurs at " + str(IntersectionCoordinates))
# else:
#     #print(nU)
#     exit(1)

##### Process results
# Return the coordinates of intersection between plane and line

IntersectionCoordinates = intersection_wrapper(sensorPlane, line1)


# Create the plot
fig = go.Figure()
fig.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ),
    title="3D Planes at z=0 and z=1"
)

# Generate graphic for planes
fig = planes_plot(fig, sensorPlane, "red")

fig = planes_plot(fig, sourcePlane, "yellow")

fig = planes_plot(fig, interPlane, "green")


# # Generate graphic for lines
fig = plot_lines(fig, line1, IntersectionCoordinates)

# Show the plot
#fig.show()

# sensorPlane.plot_area()
# plt.show()



randomPoints = sourcePlane.random_points(3)

# Plot of source plane
sourcePlane.plot_area()

# Add point markers to the plane plot
for i in range(0, len(randomPoints)):
    sourcePlane.plot_points(randomPoints[i])

plt.show()


# # Use random points to generate lines
lines = [Line((randomPoints[i][0], randomPoints[i][1], sourcePlane.position[2]), direction) for i in range(len(randomPoints) - 1)]




for i in range(len(randomPoints)-1):
    IntersectionCoordinates = intersection_wrapper(sensorPlane, lines[i])
    result = sensorArea.record_result(IntersectionCoordinates)


    # Generate graphic for lines
    # fig = plot_lines(fig, lines[i], IntersectionCoordinates)

# fig.show()