from graphicPlot import planes_plot, plot_lines
from intersectionCalculations import intersection_wrapper
from line import Line
from plane import Plane
from areas import Areas
import numpy as np
import plotly.graph_objects as go

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

fig = planes_plot(fig, sensorArea, "green")


# # Generate graphic for test line
# fig = plot_lines(fig, line1, IntersectionCoordinates)

# Show the plot
#fig.show()

# sensorPlane.plot_area()
# plt.show()



randomPoints = sourcePlane.random_points(60)
# print(randomPoints)

# randomPoints = np.array([[-0.6, 0.4], [-0.3, 0.4]])


# # Plot of source plane
# sourcePlane.plot_area()
#
# # Add point markers to the plane plot
# for i in range(0, len(randomPoints)):
#     sourcePlane.plot_points(randomPoints[i])
#
# plt.show()


# # Use random points to generate lines
lines = [Line((randomPoints[i][0], randomPoints[i][1], sourcePlane.position[2]), direction) for i in range(0, len(randomPoints))]

# Initialise hit / miss values before looping
hit = 0
miss = 0

for i in range(len(lines)):

    IntersectionCoordinates = intersection_wrapper(sensorPlane, lines[i])
    result = sensorArea.record_result(IntersectionCoordinates)

    if result == 1:
        fig = plot_lines(fig, lines[i], IntersectionCoordinates, "green")
        # print("Hit")
        hit += 1
    elif result == 0:
        fig = plot_lines(fig, lines[i], IntersectionCoordinates, "red")
        # print("Miss")
        miss += 1
    # Generate graphic for lines
    # fig = plot_lines(fig, lines[i], IntersectionCoordinates)

fig.show()

print("Total number of hits recorded = " + str(hit))
print("Total number of misses recorded = " + str(miss))