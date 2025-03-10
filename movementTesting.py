import numpy as np
import matplotlib.pyplot as plt

from arcRotation import convert_to_cartesian, arc_movement_coordinates
from main import initialise_planes_and_areas, create_lines_from_random_points, initialise_3d_plot, \
    visualise_environment, do_rotation
from plane import Plane


def convert_to_polar(x,y,z):
    """
    Received coordinates in cartesian form and converts to polar
    """

    theta = np.arctan2(y, x)
    rho = np.sqrt(x**2 + y**2 + z**2)
    phi = np.arccos(z / rho)

    polar = np.array([rho, theta, phi])

    print(f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f} -> to polar: \nRho: {polar[0]:.2f}, Theta: {np.degrees(polar[1]):.2f}°, Phi: {np.degrees(polar[2]):.2f}°")
    # print(f"Rho: {polar[0]:.2f}, Theta: {np.degrees(polar[1]):.2f}°, Phi: {np.degrees(polar[2]):.2f}°")

    return polar

def plot_spherical_coordinates(ax, polarCoords):
    """
    Converts spherical coordinates (rho, theta, phi) to Cartesian and plots them in 3D.

    Args:
        rho (float): Radius (distance from origin).
        theta (float): Azimuth angle in **radians**.
        phi (float): Elevation angle in **radians**.
    """
    n = len(polarCoords)
    for i in range(n):
        # Extract spherical coordinates
        rho, theta, phi = polarCoords[i]

        # Correct Cartesian conversion
        x = rho * np.sin(phi) * np.cos(theta)
        y = rho * np.sin(phi) * np.sin(theta)
        z = rho * np.cos(phi)

        ax.scatter(x, y, z, color='blue', alpha=(n - i) / n, s=100, label="Converted Point")

    ax.set_xlim([-polarCoords[0][0], polarCoords[0][0]])
    ax.set_ylim([-polarCoords[0][0], polarCoords[0][0]])
    ax.set_zlim([-polarCoords[0][0], polarCoords[0][0]])

def prepareFigure():
    # Create a 3D figure
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Plot reference axes
    ax.quiver(0, 0, 0, 1, 0, 0, color='r', arrow_length_ratio=0.1, label='X-axis')
    ax.quiver(0, 0, 0, 0, 1, 0, color='g', arrow_length_ratio=0.1, label='Y-axis')
    ax.quiver(0, 0, 0, 0, 0, 1, color='b', arrow_length_ratio=0.1, label='Z-axis')

    circle_theta = np.linspace(0, 2 * np.pi, 100)  # 100 points around the circle
    circle_x = np.cos(circle_theta)  # X-coordinates
    circle_y = np.sin(circle_theta)  # Y-coordinates
    circle_z = np.zeros_like(circle_x)  # Keep Z at 0 (XY-plane)

    # Plot unit circle
    ax.plot(circle_x, circle_y, circle_z, color='black', linestyle='dashed', label="Unit Circle in XY-plane")

    # Set labels and limits
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_zlabel("Z-axis")
    ax.set_title("3D Plot of Spherical Coordinates")

    return fig, ax


def main_movement_test():
    # Step 1: Initialize planes and areas
    sensorPlane, sourcePlane, interPlane, sensorArea = initialise_planes_and_areas()

    # Step 2: Create lines from source plane
    lines = create_lines_from_random_points(sourcePlane, num_points=60, direction=sourcePlane.direction)

    # Step 3: Create 3D plot and visualize environment
    fig = initialise_3d_plot(sourcePlane)
    fig = visualise_environment(fig, sensorPlane, "red")
    fig = visualise_environment(fig, sourcePlane, "yellow")

    # Step 4: Apply translation / rotation to original source plane
        # Create copy of sourcePlane
        # rotate by 90 degrees in x-axis
        # translate to desired starting position
    theta = 90 # Degrees of rotation
    translation = np.array([1, 0, -1]) # Translation vector for moving source plane

    rotationAxis = "x"

    # Create new plane be rotated / translated source plane
    new_source_plane = Plane(f"Rotated {theta:.0f}° in {rotationAxis}-axis",
                             sourcePlane.position,
                             sourcePlane.direction,
                             sourcePlane.width,
                             sourcePlane.length)

    # Apply rotation
    new_source_plane.rotate_plane(do_rotation(np.radians(theta), rotationAxis))

    # Apply translation
    new_source_plane.translate_plane(translation)

    # Visualise the new source plane
    fig = visualise_environment(fig, new_source_plane, "green")

    new_source_plane.print_pose()


    fig, ax = prepareFigure()

    # Get coordinates for P at each new position
    cartesianCoords, polarCoords = arc_movement_coordinates(30, 9)

    # Update Matlib 2D plot of positions
    plot_spherical_coordinates(ax, polarCoords)



    # Show plot
    plt.show()
    fig.show()

# convert_to_polar(0,-1,0)
# main_movement_test()

