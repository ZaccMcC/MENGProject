import numpy as np
import matplotlib.pyplot as plt
#
# from arcRotation import arc_movement_coordinates, rotation_rings, convert_to_cartesian
#
#
# def add_circle_ref(radius_circle):
#     # Generate a unit circle in the xy-plane at z=0
#     theta = np.linspace(0, 2 * np.pi, 100)
#     circle_x = np.cos(theta) * radius_circle
#     circle_y = np.sin(theta) * radius_circle
#     circle_z = np.zeros_like(theta)  # z = 0
#
#     # Plot the unit circle
#     ax.plot(circle_x, circle_y, circle_z, f"-r", linewidth=0.5, label="Unit Circle (z=0)")
#
#
# def add_hemisphere(radius_circle):
#     # Create hemisphere surface
#     phi = np.linspace(0, np.pi / 2, 30)  # Polar angle from 0 to 90 degrees (hemisphere)
#     theta = np.linspace(0, 2 * np.pi, 30)  # Azimuthal angle
#     phi, theta = np.meshgrid(phi, theta)
#
#     # Convert spherical to Cartesian coordinates
#     hemisphere_x = radius_circle * np.sin(phi) * np.cos(theta)
#     hemisphere_y = radius_circle * np.sin(phi) * np.sin(theta)
#     hemisphere_z = radius_circle * np.cos(phi)  # Positive z-values only
#
#     # Plot the hemisphere
#     ax.plot_surface(hemisphere_x, hemisphere_y, hemisphere_z, color='r', alpha=0.1,
#                     edgecolor='none')  # Semi-transparent
#
#
# def plot_cords_mat(ax, point_list, c, label):
#     """
#     Plots a list of 3D points and ensures they appear in the legend.
#
#     Args:
#         ax: Matplotlib 3D axis object.
#         point_list: List of (x, y, z) coordinates.
#         c: Color of the points.
#         label: Label for legend.
#     """
#     # Plot all points with a single scatter call
#     x_vals = [round(float(x), 2) for x, y, z in point_list]
#     y_vals = [round(float(y), 2) for x, y, z in point_list]
#     z_vals = [round(float(z), 2) for x, y, z in point_list]
#
#     # Combine points into single nested list
#     formatted_points = [[x, y, z] for x, y, z in zip(x_vals, y_vals, z_vals)]
#
#     print(f"Number of points: {len(point_list)}")
#     print(f"Point list: {formatted_points}")
#
#     # Plot points
#     ax.scatter(x_vals, y_vals, z_vals, c=c, marker='o', label=label)
#
#     ax.legend()
#
# # Spherical to Cartesian conversion
# def spherical_to_cartesian(r, theta_deg, phi_deg):
#     theta = np.radians(theta_deg)
#     phi = np.radians(phi_deg)
#     x = r * np.sin(phi) * np.cos(theta)
#     y = r * np.sin(phi) * np.sin(theta)
#     z = r * np.cos(phi)
#     return x, y, z
#
# radius = 10
# arc_angle = 90
#
# # Create a 3D plot
# fig = plt.figure(figsize=(8, 6))
# ax = fig.add_subplot(111, projection='3d')
#
# # Add reference circle and hemisphere to figure
# add_circle_ref(radius)
# add_hemisphere(radius)
#
# initial_arc = ((10, 0, 0), (0, 0, 10), (-10, 0, 0))
#
# point2 = spherical_to_cartesian(radius, 0, 45)
# print(f"Point2: {point2}")
# exit(2)
# second_arc = ((10, 0, 0), point2, (-10, 0, 0))
#
#
# # Add points to ax from cartesian points list
# plot_cords_mat(ax, initial_arc, "blue", f"Level: 1")
# plot_cords_mat(ax, second_arc, "red", f"Level: 1")
#
# # Labels
# ax.set_xlabel('X Axis')
# ax.set_ylabel('Y Axis')
# ax.set_zlabel('Z Axis')
# ax.set_title(f"All arc movement plane positions \n (r, θ, φ) = ({radius}, {arc_angle}, φ)")
#
# plt.legend()
# # Show the plot
# plt.show()

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


def plot_arc(arc, label, color):
    ax.plot(arc[0], arc[1], arc[2], label=label, color=color)


# Generate points for the original arc in the x-z plane
num_points = 100
theta_arc = np.linspace(0, np.pi, num_points)  # 0 to pi radians
radius = 10

# Original arc (x-z plane)
x_orig = radius * np.cos(theta_arc)
y_orig = np.zeros_like(x_orig)
z_orig = radius * np.sin(theta_arc)

# Stack into array for transformation
original_arc = np.vstack((x_orig, y_orig, z_orig))

# Rotation around x-axis by 45 degrees
angle_deg = 45
angle_rad = np.radians(angle_deg)
rotation_matrix_x = np.array([
    [1, 0, 0],
    [0, np.cos(angle_rad), -np.sin(angle_rad)],
    [0, np.sin(angle_rad), np.cos(angle_rad)]
])

# Apply rotation
rotated_arc = rotation_matrix_x @ original_arc

# Plotting
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
add_hemisphere(radius)



plot_arc(original_arc, 'Original Arc (x-z plane)', 'green')

plot_arc(rotated_arc, 'Rotated Arc (45° about x-axis)', 'orange')


# Endpoints and midpoint markers
ax.scatter([10, -10, 0], [0, 0, 0], [0, 0, 10], color='blue', marker='o')  # Original points
mid_rotated = rotation_matrix_x @ np.array([[0], [0], [10]])
ax.scatter(0, mid_rotated[1], mid_rotated[2], color='orange', marker='^')  # Rotated midpoint

# Labels and legend
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Arc Rotation Around X-Axis')
ax.legend()
ax.set_box_aspect([1,1,1])  # Equal aspect ratio

plt.tight_layout()
plt.show()