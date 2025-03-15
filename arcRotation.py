import logging

import numpy as np


def convert_to_cartesian(rho, theta, phi):
    """
    Converts spherical coordinates (rho, theta, phi) back to Cartesian (x, y, z).

    Args:
        rho (float): Radius (distance from origin).
        theta (float): Azimuth angle in **radians**.
        phi (float): Elevation angle in **radians**.

    Returns:
        np.array: Cartesian coordinates [x, y, z].
    """
    x = rho * np.sin(phi) * np.cos(theta)
    y = rho * np.sin(phi) * np.sin(theta)
    z = rho * np.cos(phi)

    cartesian = np.array([x, y, z])

    # print(f"X: {cartesian[0]:.2f}, Y: {cartesian[1]:.2f}, Z: {cartesian[2]:.2f}")

    return cartesian


def arc_movement_coordinates(radius, theta_angle, phi_angle=90):
    """
    Takes input angle for arc rotation and returns cartesian coordinates for each position.

    :param:
        theta_angle: Increment angle for arc rotation, angle by which plane is rotated around global origin
        radius: Radius of arc rotation

    :returns:
        cartesianCoords (np.array): Contains cartesian coordinates for each position.
        polarCoords (np.array): Contains polar coordinates for each position.
    """
    # Predefine array to store output cartesian coords
    cartesianCoords = []
    polarCoords = []

    # Calculate the positions around the xy axis for arc rotation

    thetas = np.arange(0, 360, theta_angle)  # Generate values for theta at each increment
    for idx, i in enumerate(thetas):
        polar = [radius, np.radians(i),
                 np.radians(phi_angle)]  # Each position around the arc rotation, has coordinate defined in polar form

        # Store polar coords
        polarCoords.append(polar)
        # Convert polar form to cartesian form
        cartesian = convert_to_cartesian(polar[0], polar[1], polar[2])
        cartesianCoords.append(cartesian)

        cartesian_str = f"Position {idx}: X: {cartesian[0]:.2f}, Y: {cartesian[1]:.2f}, Z: {cartesian[2]:.2f}"
        # print(f"{cartesian_str}")

    print("")

    return cartesianCoords, polarCoords

def rotation_rings(phis, radius, theta_angle):

    all_points = []
    allPositions_polar = []
    i = 0
    for phi_angles in phis:
        # Returns coordinates around circle
        list_point, list_points_polar = arc_movement_coordinates(radius, theta_angle, phi_angles)
        # Extend the all_points list with the new points
        all_points.extend(list_point)  # list_point is a list of numpy arrays
        allPositions_polar.extend(list_points_polar)

        logging.debug(f"For phi angle {phi_angles}, generated {len(list_point)} points")
        i = i + 1

    # Convert the list of arrays
    all_points = np.array(all_points)
    allPositions_polar = np.array(allPositions_polar)

    logging.debug(f"Generated {len(all_points)} points for rotation rings \n")

    return all_points, allPositions_polar

def arc_movement_vector(plane_object, coords):
    """
    Gets current position of plane and calculates new position after rotation.
    :arg plane_object
        coords (np.array): Contains cartesian coordinates for next position.
    :return: translationVector (np.array): Contains vector from current position to new position.
    """
    # translationVector = plane_object.position - coords # Incorrect
    translationVector = coords - plane_object.position

    return translationVector
