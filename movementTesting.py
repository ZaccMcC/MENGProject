import numpy as np
import matplotlib.pyplot as plt

from arcRotation import arc_movement_coordinates, rotation_rings, convert_to_cartesian


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


def plot_cords_mat(ax, point_list, c, label):
    """
    Plots a list of 3D points and ensures they appear in the legend.

    Args:
        ax: Matplotlib 3D axis object.
        point_list: List of (x, y, z) coordinates.
        c: Color of the points.
        label: Label for legend.
    """
    # Plot all points with a single scatter call
    x_vals = [round(float(x), 2) for x, y, z in point_list]
    y_vals = [round(float(y), 2) for x, y, z in point_list]
    z_vals = [round(float(z), 2) for x, y, z in point_list]

    # Combine points into single nested list
    formatted_points = [[x, y, z] for x, y, z in zip(x_vals, y_vals, z_vals)]

    print(f"Number of points: {len(point_list)}")
    print(f"Point list: {formatted_points}")

    # Plot points
    ax.scatter(x_vals, y_vals, z_vals, c=c, marker='o', label=label)

    ax.legend()


radius = 9
arc_angle = 90

# Create a 3D plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Add reference circle and hemisphere to figure
add_circle_ref(radius)
add_hemisphere(radius)

# Define array of phi angles to generate points at
phis = np.arange(90, -90, -30)  # Generate values for theta at each increment
colours = ["b", "g", "r", "y","b", "g", "r", "y"]


# arc_phi_angle = np.arange(90, -30, -30)
# arc_theta_angle = 60
# sequence_ID = 0

arc_theta_angle = np.arange(90, -30, -30)
arc_phi_angle = 60
sequence_ID = 1


phis = np.arange(90, -120, -30)
theta = np.zeros(len(phis))
r = np.ones(len(phis)) * radius

print(f"Phi: {phis} shape = {phis.shape}")
print(f"Theta: {theta}")
print(f"R: {r}")




# Make a loop through each phi angle
i = 0
for idx, phi_angles in enumerate(phis):
    # Returns coordinates around circle


    # all_positions, all_positions_polar = rotation_rings(
    #     sequence_ID,
    #     radius,  # Radius of arc movement
    #     arc_theta_angle,# steps of theta taken around the arc
    #     arc_phi_angle  # phi levels to the spherical arc
    # )

    cartesian_coords = convert_to_cartesian(r[idx], np.radians(theta[idx]), np.radians(phi_angles))
    all_positions = [tuple(cartesian_coords)]  # Convert to a list of one tuple



    print(f"For current phi angle: {phi_angles}")

    arc_radius = radius * np.sin(np.radians(phi_angles))
    print(f"Arc radius: {round(arc_radius,2)}")

    # Add points to ax from cartesian points list
    plot_cords_mat(ax, all_positions, colours[i], f"Level: {i} φ: {phi_angles}")

    i = i + 1


# Labels
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title(f"All arc movement plane positions \n (r, θ, φ) = ({radius}, {arc_angle}, φ)")

plt.legend()
# Show the plot
plt.show()
