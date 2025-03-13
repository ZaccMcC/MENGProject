import numpy as np
import matplotlib.pyplot as plt

from arcRotation import arc_movement_coordinates


def add_circle_ref(radius_circle):
    # Generate a unit circle in the xy-plane at z=0
    theta = np.linspace(0, 2 * np.pi, 100)
    circle_x = np.cos(theta) * radius_circle
    circle_y = np.sin(theta) * radius_circle
    circle_z = np.zeros_like(theta)  # z = 0

    # Plot the unit circle
    ax.plot(circle_x, circle_y, circle_z, f"-r", linewidth=0.5, label="Unit Circle (z=0)")


def plot_cords_mat(point_list, c):
    for x, y, z in point_list:
        x = round(x, 2)
        y = round(y, 2)
        z = round(z, 2)
        print(f"x: {x}, y: {y}, z: {z}")
        # Scatter plot of the points
        ax.scatter(x, y, z, c=f"{c}", marker='o')


list_points1 = np.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])
radius = 9
arc_angle = 25

# Create a 3D plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Add reference circle to figure
add_circle_ref(radius)

# Returns coordinates around circle
list_point, allPositions_polar = arc_movement_coordinates(radius, arc_angle)
# Add points to ax from cartesian points list
plot_cords_mat(list_point, "b")

# Returns coordinates around circle
list_point, _ = arc_movement_coordinates(radius, arc_angle, 45)
# Add points to ax from cartesian points list
plot_cords_mat(list_point, "b")

# Labels
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('3D Scatter Plot')

# Show the plot
plt.show()
