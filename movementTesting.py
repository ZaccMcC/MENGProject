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


def add_hemisphere(radius_circle):
    # Create hemisphere surface
    phi = np.linspace(0, np.pi / 2, 30)  # Polar angle from 0 to 90 degrees (hemisphere)
    theta = np.linspace(0, 2 * np.pi, 30)  # Azimuthal angle
    phi, theta = np.meshgrid(phi, theta)

    # Convert spherical to Cartesian coordinates
    hemisphere_x = radius_circle * np.sin(phi) * np.cos(theta)
    hemisphere_y = radius_circle * np.sin(phi) * np.sin(theta)
    hemisphere_z = radius_circle * np.cos(phi)  # Positive z-values only

    # Plot the hemisphere
    ax.plot_surface(hemisphere_x, hemisphere_y, hemisphere_z, color='r', alpha=0.1,
                    edgecolor='none')  # Semi-transparent


def plot_cords_mat(point_list, c):
    for x, y, z in point_list:
        x = round(x, 2)
        y = round(y, 2)
        z = round(z, 2)
        # print(f"x: {x}, y: {y}, z: {z}")
        # Scatter plot of the points
        ax.scatter(x, y, z, c=f"{c}", marker='o')


radius = 9
arc_angle = 25

# Create a 3D plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Add reference circle and hemisphere to figure
add_circle_ref(radius)
add_hemisphere(radius)

# Define array of phi angles to generate points at
phis = np.arange(90, -30, -30)  # Generate values for theta at each increment
colours = ["b", "g", "b", "r"]

# Make a loop through each phi angle
i = 0
for phi_angles in phis:
    # Returns coordinates around circle
    list_point, allPositions_polar = arc_movement_coordinates(radius, arc_angle, phi_angles)
    # Add points to ax from cartesian points list
    plot_cords_mat(list_point, colours[i])

    i = i + 1

# # Returns coordinates around circle
# list_point, _ = arc_movement_coordinates(radius, arc_angle, 45)
# # Add points to ax from cartesian points list
# plot_cords_mat(list_point, "g")

# Labels
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('3D Scatter Plot')

# Show the plot
plt.show()
