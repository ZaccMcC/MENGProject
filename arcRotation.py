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

    print(f"Arc movement coordinates: radius = {radius}, theta = {theta_angle}, phi = {phi_angle}")

    # Calculate the positions around the xy axis for arc rotation

    thetas = np.arange(0, 360, theta_angle)  # Generate values for theta at each increment
    print(f"Vary theta, at constant phi: angle_steps = {thetas}")
    for idx, i in enumerate(thetas):
        polar = [radius, np.radians(i),
                 np.radians(phi_angle)]  # Each position around the arc rotation, has coordinate defined in polar form

        # Store polar coords
        polarCoords.append(polar)
        # Convert polar form to cartesian form
        cartesian = convert_to_cartesian(polar[0], polar[1], polar[2])
        cartesianCoords.append(cartesian)

    print(f"Polar coordinates: {polarCoords}")

    return cartesianCoords, polarCoords

def get_arc_coordinates(sequence_ID, radius, constant_angle, stepping_angle):
    """
    - Takes radius, and two angles
    - Makes a list of polar coordinates between 0 degrees and 180 / 360, in steps of stepping_angle,
        at constant radius and constant other input angle
    - Converts polar coordinates to cartesian coordinates
    - Returns cartesian & polar coordinates for each position
    :param:
        sequence_ID: 1 for varying theta, 2 for varying phi
        radius
        constant_angle
        stepping_angle

    :return:
    """
    # Holds the output angles
    cartesianCoords = []
    polarCoords = []

    if sequence_ID == 2:  # Vary theta, at constant phi: angle_steps = {angle_steps}

        # Define angle steps
        angle_steps = np.arange(0, 360, stepping_angle)
        logging.debug(f"Angle steps: {angle_steps}")
        print(f"Vary theta, at constant phi: angle_steps = {angle_steps}")

        for steps in angle_steps:
            # For varying theta: [radius, theta (varying), phi (constant)]
            polar = [radius, np.radians(steps), np.radians(constant_angle)]

            # Store polar coords
            polarCoords.append(polar)

            # Convert polar form to cartesian form
            cartesianCoords.append(convert_to_cartesian(polar[0], polar[1], polar[2]))

    if sequence_ID == 1:  # Vary phi, at constant theta: angle_steps = {angle_steps}
        angle_steps = np.arange(90, -90, -stepping_angle)

        for steps in angle_steps:
            # For varying phi: [radius, theta (constant), phi (varying)]
            polar = [radius, np.radians(constant_angle), np.radians(steps)]

            # Store polar coords
            polarCoords.append(polar)

            # Convert polar form to cartesian form
            cartesianCoords.append(convert_to_cartesian(polar[0], polar[1], polar[2]))

    return cartesianCoords, polarCoords


def rotation_rings(sequence_ID, radius, angle_theta, angle_phi):
    """
    Create a list of points around the arc rotation, and return cartesian coordinates for each position.
    Directly generate list of secondary angles for arc rotation, and return cartesian coordinates for each position.
    """
    all_points = []
    allPositions_polar = []
    i = 0

    if sequence_ID == 2: # Get variations of theta, for each value of phi
        logging.debug(f"Phi angles {angle_phi}")

        for phi_angles in angle_phi:

            # Returns coordinates around circle
            list_point, list_points_polar = get_arc_coordinates(sequence_ID, radius, phi_angles, angle_theta)

            # Extend the all_points list with the new points
            all_points.extend(list_point)  # list_point is a list of numpy arrays
            allPositions_polar.extend(list_points_polar)

            logging.debug(f"For phi angle {phi_angles}, generated {len(list_point)} points")

            i = i + 1

    if sequence_ID == 1:
        for theta_angles in angle_theta:

            # Returns coordinates around circle
            list_point, list_points_polar = get_arc_coordinates(sequence_ID, radius, theta_angles, angle_phi)

            # Extend the all_points list with the new points
            all_points.extend(list_point)  # list_point is a list of numpy arrays
            allPositions_polar.extend(list_points_polar)

            logging.debug(f"For theta angle {theta_angles}, generated {len(list_point)} points")
            i = i + 1

    # Convert the list of arrays
    all_points = np.array(all_points)
    allPositions_polar = np.array(allPositions_polar)

    logging.debug(f"Generated {len(all_points)} points for rotation rings \n")

    for i in range(len(all_points)):
        print(f"Point {i}: ({np.round(all_points[i][0], 2)}, {np.round(all_points[i][1], 2)}, {np.round(all_points[i][2], 2)})"
              f" ({allPositions_polar[i][0]}, {np.round(np.degrees(allPositions_polar[i][1]),2)}, {np.round(np.degrees(allPositions_polar[i][2]),2)})")

    return all_points, allPositions_polar[:, sequence_ID]

def arc_movement_vector(plane_object, coords):
    """
    Gets current position of plane and new position after and calculates the vector between them

    :arg: plane_object
        plane_object (Plane): Contains position and orientation of plane.
        coords (np.array): Contains cartesian coordinates for next position.
    :return: translationVector (np.array): Contains vector from current position to new position.
    """
    # translationVector = plane_object.position - coords # Incorrect
    translationVector = coords - plane_object.position

    return translationVector
