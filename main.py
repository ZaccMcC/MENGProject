from memory_profiler import profile
import random
from arcRotation import arc_movement_vector, rotation_rings
from intersectionCalculations import intersection_wrapper  # Import for calculating line-plane intersection
from line import Line  # Import for Line object
from plane import Plane  # Import for Plane object
from areas import Areas  # Import for target areas
import numpy as np  # For mathematical operations
import plotly.graph_objects as go  # For 3D visualization

import logging
from config import config


# Valid logging levels "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"


def initialise_planes_and_areas():
    """
Initialises all planes and the target area.
Returns: sensorPlane, sourcePlane, aperturePlane, and sensorArea
"""

    # Define the source plane
    # Defines its position (centre point), its direction (facing down)
    sourcePlane = Plane("Source Plane", **config.planes["source_plane"])

    # Define the sensor plane
    sensorPlane = Plane("Sensor Plane", **config.planes["sensor_plane"])

    # Define the intermediate plane
    aperturePlane = Plane("Aperture Plane", **config.planes["aperture_plane"])

    # Extract sensor keys from JSON file
    sensor_keys = config.sensor_areas.keys()

    # Define the sensor area (target area on the sensor plane)
    sensorAreas = [Areas(**config.sensor_areas[sensor]) for sensor in sensor_keys]

    # Extract aperture keys from JSON aperture_areas
    aperture_keys = config.aperture_areas.keys()
    apertureAreas = [Areas(**config.aperture_areas[aperture]) for aperture in aperture_keys]

    return sensorPlane, sourcePlane, aperturePlane, sensorAreas, apertureAreas


def initialise_3d_plot(sensorPlane):
    """
    Initialises a 3D plot using Plotly.
    Generates a global axis for the plot.

    Returns: A Plotly figure object.
    """
    lims = 20
    fig = go.Figure()
    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode="cube",  # Ensures uniform scaling
            xaxis=dict(title="X-Axis", range=[-lims, lims]),  # Set equal ranges
            yaxis=dict(title="Y-Axis", range=[-lims, lims]),  # Adjust based on your data
            zaxis=dict(title="Z-Axis", range=[-lims, lims])  # Keep Z range similar
        ),
        title="3D Planes and Lines visualization"

    )

    global_axis = [sensorPlane.right, sensorPlane.up, sensorPlane.direction]

    axis_colours = ['red', 'green', 'blue']
    axis_names = ['Right (x)', 'Up (y)', 'Normal (z)']

    for i in range(3):
        unit_vector = global_axis[i] / np.linalg.norm(global_axis[i])  # Normalize
        start = np.array([0, 0, 0])  # Origin of local axes at plane's position
        end = 0 + unit_vector  # Unit length

        fig.add_trace(go.Scatter3d(
            x=[start[0], end[0]],
            y=[start[1], end[1]],
            z=[start[2], end[2]],
            mode='lines+markers',
            line=dict(color=axis_colours[i], width=5),
            marker=dict(size=8, color=axis_colours[i], opacity=0.8),
            name=f"{axis_names[i]}",
            showlegend=True,
            hovertext=[f"Global axis: {axis_names[i]}"]  # Appears when hovering
        ))

    fig.update_traces(showlegend=True)
    return fig


def visualise_environment(fig, planeObject, colour):  # sensorPlane, sourcePlane, aperturePlane, sensorArea):
    """
    Adds planes and areas to the 3D plot for visualization.
    Returns: Updated Plotly figure.
    """
    fig = planeObject.planes_plot_3d(fig, colour)
    return fig


def update_lines_global_positions(lines, new_source_plane):
    """
    Updates the global positions of all lines based on their local positions within new source plane.
    :return:
        lines: new list of lines with updated global positions.
    """
    # Initialize their global positions based on the plane
    for line in lines:
        line.update_global_position(new_source_plane)
        line.direction = new_source_plane.direction

    return lines


def create_lines_from_plane(source_plane, num_lines):
    """
    Generates random line positions in the plane's local coordinate system.

    Args:
        source_plane (Plane): The source plane object.
        num_lines (int): Number of lines to generate.

    Returns:
        list: List of Line objects.
    """
    local_positions = source_plane.random_points(num_lines)  # Local coordinates
    # print(f"Local positions: {local_positions}")
    # print(f"Number of lines: {len(local_positions)}")

    lines = [
        Line([x, y, 0], source_plane.direction, line_id=idx)
        for idx, (x, y) in enumerate(local_positions)
    ]

    return lines


def intersection_checking(targetArea, intersection_coordinates):
    """
    Gets input of target areas and coordinate of intersection
    Checks if the intersection point is in the target area.
    """
    result = None

    for target in targetArea:
        # Check if the intersection point is in the target area
        result = target.record_result(intersection_coordinates)
        # logging.debug(f"Checking intersection with {target.title}...")

        if result == 1:  # Hit occurs
            return 1, target
    if result == 0:  # Miss
        return 0, 0
    else:
        return -1, 0


def evaluate_line_results(sensorPlane, sensorArea, aperturePlane, apertureAreas, lines):
    """
    Checks intersections of lines with the sensor plane and evaluates whether they hit the target area.

    Updates line object internal parameters with the results.

    Args:
        sensorPlane: The plane intersecting with the lines.
        sensorArea: List of all sensor objects - target areas to evaluate hits.
        aperturePlane:
        apertureAreas:
        lines: List of Line objects.

    Returns:
        hit: number of hits.
        miss: number of misses.
    """
    hit = 0
    miss = 0
    hit_list = []
    miss_list = []

    # Reset previous sensor illumination values
    for sensors in sensorArea:
        sensors.illumination = 0

    for line in lines:
        line.result = 0
        # Calculate intersection between the line and the aperture plane
        aperture_intersection_coordinates = intersection_wrapper(aperturePlane, line)
        # Set intersection coordinate of line object
        line.intersection_coordinates = aperture_intersection_coordinates

        # Check if intersection with apertures
        aperture_intersection, _ = intersection_checking(apertureAreas, aperture_intersection_coordinates)
        if aperture_intersection == 1:  # Hit, at apertures

            # Get intersection coordinates with sensor plane
            sensor_intersection_coordinates = intersection_wrapper(sensorPlane, line)

            # Check intersection with sensor areas
            sensor_intersection, sensor = intersection_checking(sensorArea, sensor_intersection_coordinates)
            line.intersection_coordinates = sensor_intersection_coordinates

            if sensor_intersection == 1:  # Intersection occurs at sensor
                hit, line.result, sensor.illumination = hit + 1, 1, sensor.illumination + 1

                hit_list.append(line.line_id)

                continue  # Move to next line
            if sensor_intersection == 0:
                miss += 1

                miss_list.append(line.line_id)

                continue
        else:

            miss += 1
            miss_list.append(line.line_id)
            continue

    return hit, miss, hit_list, miss_list


def handle_results(sensor_objects):
    """
    Handles the results from intersection calculations
    Args:
        sensor_objects: List of all sensor objects

    Returns:

    """
    for sensors in sensor_objects:
        if sensors.illumination != 0:
            logging.debug(f"{sensors.title} was illuminated")
        else:
            logging.debug(f"Sensor {sensors.title} was not illuminated")


def do_rotation(theta, axis):
    """
    Gets rotation matrix for specified axis and angle.

    Args:
        theta: The angle of rotation in radians.
        axis: The axis of rotation.

    Returns:
        The rotation matrix for the specified axis and angle.
    """

    if axis == "x":
        R = np.array([
            [1, 0, 0],
            [0, np.cos(theta), - np.sin(theta)],
            [0, np.sin(theta), np.cos(theta)]
        ])
    elif axis == "y":
        R = np.array([
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)]
        ])
    elif axis == "z":
        R = np.array([
            [np.cos(theta), - np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])
    else:
        print("Invalid axis")
        R = np.array([1, 1, 1])
    return R


def rotation_test(angle, axis, vectors):
    """
    Test function for rotation matrix.
    :param angle:
    :param axis:
    :param vectors:
    :return:
        Print rotation matrix.
    """

    rotation_matrix = do_rotation(angle, axis)

    # print(f"Rotation matrix for {axis} axis: \n{rotation_matrix}")
    print(f"Rotation about {axis} axis by {np.degrees(angle)}° {angle} rad")
    for vector in vectors:
        rotated_vector = np.dot(rotation_matrix, vector)
        print(f"{vector} rotated -> {np.round(rotated_vector, 2)}")


def setup_initial_pose(source_plane, theta, rotation_axis, all_positions):
    """
    Sets up the initial position and orientation of the plane before it starts moving along the arc.

    1. Creates copy of the source plane.
    2. Applies an initial rotation to the alight the plane
    3. Translates the plane to the starting position for the arc

    Args:
        source_plane (Plane): The original source plane from which movement begins.
        theta (float): The rotation angle (in degrees) applied before movement.
        rotation_axis (str): The axis of rotation.
        all_positions (list): Contains all positions around the arc

    Returns:
        Plane: The transformed plane at the starting position of the arc.
    """

    # Create a copy of the source plane
    start_pose_plane = Plane(
        f"Copy of source",
        source_plane.position,
        source_plane.direction,
        source_plane.width,
        source_plane.length
    )

    # Before movement, print initial pose
    start_pose_plane.print_pose()

    # Apply initial rotation to align normal vector
    start_pose_plane.rotate_plane(do_rotation(np.radians(theta), rotation_axis))
    start_pose_plane.title = f"Plane rotated {theta:.0f}° in {rotation_axis}-axis"
    start_pose_plane.print_pose()

    # Set position to the first computed arc position instead of translating manually
    logging.debug(f"Moving to initial arc position: {np.round(all_positions[0], 2)}")

    # start_pose_plane.position = np.array(all_positions[0])

    translation_vector = arc_movement_vector(start_pose_plane, all_positions[0])
    start_pose_plane.translate_plane(translation_vector)

    start_pose_plane.title = "Plane moved to initial arc position"
    start_pose_plane.print_pose()

    return start_pose_plane


def generate_arc_animation(fig, rotated_planes, lines_traces, results):
    """
    Generates an animated visualization of the arc movement.

    Data type notes --
        Plane trace is type list, shape (length rotated_planes,)
        Plane trace [0] type: <class 'plotly.graph_objs._mesh3d.Mesh3d'>: shape ()
        Axis trace is type list, shape (length rotated_planes, 3)
        Axis trace [0] type: <class 'list'>: shape (3,)
        Line trace is type list, shape (length rotated_planes, 2)
        Line trace [0] type: <class 'list'>: shape (2,)

    Args:
        fig (Plotly Figure): The figure used for visualization.
        rotated_planes (list): The list of planes from move_plane_along_arc().
        lines_traces (list): List of Line objects for each plane.
        results:
    Returns:
        fig (Plotly Figure): Updated figure with animation.
    """
    plane_trace = []
    axis_traces = []
    frame_titles = list(np.zeros(len(rotated_planes)))

    num_frames = len(rotated_planes)

    for idx, plane in enumerate(rotated_planes):
        # Debugging - Check if planes are being added
        logging.debug(f"Preparing elements for frame {idx} for plane at position {plane.position}")

        # Get plane and axis traces
        plane_trace.append(plane.planes_plot_3d(go.Figure(), "yellow").data[
                               0])  # makes plane_trace[idx] type = "plotly.graph_objs._mesh3d.Mesh3d"
        axis_traces.append(list(plane.plot_axis(go.Figure()).data))  # makes axis_traces[idx] type = "tuple"

        frame_titles[idx] = f"Position {idx} - Hits {results[idx][0]:.0f}, Misses {results[idx][1]:.0f} "

    # check_fig_data(fig)

    for traces in fig.data:
        fig.add_trace(traces)

    # Prepare the actual frames
    frames = [
        go.Frame(
            data=[
                plane_trace[i],  # Single plane
                *axis_traces[i],  # Three axis traces
                *lines_traces[i],  # Two line traces
            ],
            name=f"Frame {i}",
            layout=go.Layout(title=frame_titles[i])
        )
        for i in range(num_frames)
    ]

    # Add animation controls
    fig.update_layout(
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                    "label": "▶ Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "⏸ Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }],
        # Add a slider for manual frame selection
        sliders=[{
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 16},
                "prefix": "Position: ",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                {
                    "args": [
                        [f"Frame {k}"],
                        {"frame": {"duration": 300, "redraw": True},
                         "mode": "immediate",
                         "transition": {"duration": 300}}
                    ],
                    "label": str(k),
                    "method": "animate"
                }
                for k in range(num_frames)
            ]
        }]
    )

    # Set the frames to the figure
    fig.frames = frames

    return fig


def generate_static_arc_plot(fig, rotated_planes, line_objects):
    """
    Generates a static 3D plot of all plane positions in the arc.

    Args:
        fig (Plotly Figure): The figure used for visualization.
        rotated_planes (list): The list of planes from move_plane_along_arc().
        line_objects (list): 2D list, containing a list of Line objects for each plane.

    Returns:
        fig (Plotly Figure): Updated figure with static planes plotted.
    """

    for idx, plane in enumerate(rotated_planes):
        if idx == 0:
            fig = plane.planes_plot_3d(fig, "yellow")
        else:
            fig = plane.planes_plot_3d(fig, "blue")

        fig = plane.plot_axis(fig)  # Adds axis vectors

        # logging.debug(f"Adding line traces for plane {idx}")
        for line in line_objects[idx]:
            fig.add_trace(line)

    return fig


def plane_pose_initialisation(original_plane):
    """
    Creates a copied plane object for initial pose.
    :arg:
        original_plane: Plane object to be copied.
    :return:
        new_plane: Copied plane object.
    """
    new_plane = Plane(f"New plane", original_plane.position, original_plane.direction, original_plane.width,
                      original_plane.length)
    new_plane.right, new_plane.up, new_plane.direction = original_plane.right, original_plane.up, original_plane.direction

    return new_plane


def calculate_rotation_matrix(position, direction):
    """
    Takes input position and direction to calculate arbitrary rotation matrix.
    Using Rodrigues' rotation formula.
    :arg:
        position (3x1 matrix): Position vector.
        direction (3x1 matrix): Direction vector.
        idx (int): Plane index. Used for logging.
    :return:
        R (3x3 matrix): Rotation matrix.
        required_angle (float): Angle (rad) of rotation in calculated arbitrary rotation matrix.
    """

    logging.debug("Calculating new rotation matrix")
    # Calculate target local z axis
    target_z = np.array([0, 0, 0]) - position
    # Normalized z-direction
    target_z_norm = target_z / np.linalg.norm(target_z, keepdims=True)

    # Calculate axis of rotation
    required_rotation_axis = np.cross(direction, target_z_norm)
    normalised_axis = required_rotation_axis / np.linalg.norm(required_rotation_axis, keepdims=True)

    # Calculate angle of rotation
    required_angle = np.arccos(np.clip(np.dot(direction, target_z_norm), -1.0, 1.0))

    ## Apply Rodrigues' rotation formula
    # Compute skew-symmetric cross-product matrix of rotation_axis
    K = np.array([
        [0, -normalised_axis[2], normalised_axis[1]],
        [normalised_axis[2], 0, -normalised_axis[0]],
        [-normalised_axis[1], normalised_axis[0], 0]
    ])

    # Rodrigues' rotation formula
    R = (
            np.eye(3) +
            np.sin(required_angle) * K +
            (1 - np.cos(required_angle)) * np.dot(K, K)
    )

    return R, required_angle


def determine_movement_type(idx, sequence_ID, secondary_angle):
    """
    Checks for movement type
    Simplified logic from previous implementation
    :arg:
        idx (int): Plane index. Used for logging.
        sequence_ID (int): Indicates type of movement sequence. (2 = horizontal circles, or 1 = vertical circles)
        secondary_angle (list): Contains list of angles (ID = 2/1, theta/phi) from the polar coordinates of each position.
    :return:
        1 = First position
        2 = Horizontal circles
        3 = Same meridian
        4 = Different meridian

        None = Problem
    """
    if idx == 0:
        # First position
        return 1
    elif sequence_ID == 2:
        # Horizontal circles
        return 3
    elif sequence_ID == 1:
        # Vertical circles
        if secondary_angle[idx - 1] == secondary_angle[idx]:
            # Same meridian
            return 3
        else:
            # Different meridian
            return 2

    return None


def initialise_new_circle(plane, position):
    """
    Creates a copy of a plane, calculates translation vector and applies it to the plane, moving it to the next position.

    :arg:
        plane (Plane): Plane object.
        position (3x1 matrix): Position vector.
        direction (3x1 matrix): Direction vector.
        idx (int): Plane index. Used for logging.
    :return:
    """
    # Create copy of a plane
    new_plane = plane_pose_initialisation(plane)

    # Calculate new translation vector
    translation_vector = arc_movement_vector(new_plane, position)

    # Apply translation
    new_plane.translate_plane(translation_vector)

    return new_plane


def primary_rotation_handling(sequence_ID, new_plane, next_position, required_angle, rotation_axis):
    """
    Handles the differing primary rotation mechanisms depending on type of movement sequence.
        For vertical circles, the primary rotation matrix has to be generated for each new circle (about arbitrary axis).
        For horizontal circles, the primary rotation matrix is standard about a defined axis.

    :return:
        primary_axis
        required_angle
        plane (object)
    """
    R_p = None
    # required_angle = None

    if sequence_ID == 1:  # Vertical circles
        R_p, required_angle = calculate_rotation_matrix(next_position, new_plane.direction)
        logging.debug(
            f"Required angle for new primary rotations: {np.round(np.degrees(required_angle), 2)}° about arbitrary axis")

    elif sequence_ID == 2:  # Horizontal circles
        # Apply rotation to align with the origin in the z axis
        R_p = do_rotation(required_angle, rotation_axis[0])
        logging.debug(f"Rotating {np.round(np.degrees(required_angle), 2)}° around {rotation_axis[0]}-axis")

    return R_p, required_angle, new_plane


def move_plane_along_arc(start_plane, all_positions, primary_angle, rotation_axis, secondary_angle, sequence_ID):
    """
    Moves the plane along a predefined arc while updating line positions.

    Args:
        start_plane (Plane): A plane object representing the initial position and orientation.

        all_positions (list): A list of position vectors [x, y, z] corresponding to the points along the arc where the plane will be moved.
            Each item in this list represents a point in 3D space.

        primary_angle (float): Rotation angle applied at each step (radians) by which to increment the plane's orientation.

        rotation_axis (list): Specifies the axes about which the planes rotate at each step.

        secondary_angle (list): Contains list of angles (theta / phi, where ID = 2/1) from the polar coordinates of each position.

        sequence_ID (int): Indicates type of movement sequence. (2 = horizontal circles, or 1 = vertical circles)

    Returns:
        rotated_planes (list): Transformed plane objects at each step.
        fig (Plotly figure): Updated visualization.
    """

    rotated_planes = []

    R_p = None

    # exit(2)
    for idx, position in enumerate(all_positions):
        logging.info(f"Performing arc movement {idx}")

        if sequence_ID == 3:
            logging.debug(f"Step {idx}: Rigid arc facing origin")

            if idx == 0:
                new_plane = initialise_new_circle(start_plane, position)
                new_plane.title = f"Plane {idx} - Start"
            else:
                new_plane = initialise_new_circle(rotated_planes[idx - 1], position)
                new_plane.title = f"Plane {idx}"

                # Calculate rotation to face origin
                R, angle = calculate_rotation_matrix(position, new_plane.direction)
                new_plane.rotate_plane(R)
                logging.debug(f"Plane {idx} rotated {np.round(np.degrees(angle), 2)}° to face origin")

            rotated_planes.append(new_plane)
            new_plane.print_pose()
            continue  # Skip other movements

        movement_type = determine_movement_type(idx, 1, secondary_angle)

        logging.debug(f"Movement type: {movement_type}")
        # Movement types:
        # 1 = First position
        # 2 = Horizontal circles
        # 3 = Same meridian
        # 4 = Different meridian
        logging.debug(f"Current secondary angle: {np.round(np.degrees(secondary_angle[idx]), 2)}°")

        if movement_type is None:
            logging.error(f"Error: Unable to determine movement type for position {idx}")
            return None

        elif movement_type == 1:

            logging.debug(f"Step {idx}: First position")

            # Create copy of original plane and translate it to new position
            new_plane = initialise_new_circle(start_plane, position)
            new_plane.title = f"Plane {idx} - New Circle"

            # Set primary rotation matrix
            R_p = do_rotation(primary_angle, rotation_axis[0])

            logging.debug(
                f"Primary rotation matrix set by {np.round(np.degrees(primary_angle), 2)}° / {np.round(primary_angle, 2)} rad about {rotation_axis[0]}-axis")
            logging.debug(f"Primary matrix: \n{np.round(R_p, 2)} \n")


        elif movement_type == 2:

            logging.debug(f"Step {idx}: Different meridian")

            # Create copy of original plane and translate it to new position
            new_plane = initialise_new_circle(start_plane, position)
            new_plane.title = f"Plane {idx} - New Circle"

            secondary_rotation_angle = secondary_angle[idx]
            logging.debug(
                f"Current secondary angle {np.round(np.degrees(secondary_angle[idx]), 2)}° previous {np.round(np.degrees(secondary_angle[idx - 1]), 2)}°")

            # Get secondary rotation matrix
            R_s = do_rotation(secondary_rotation_angle, rotation_axis[1])

            # Apply secondary rotation matrix
            new_plane.rotate_plane(R_s)

            logging.debug(
                f"Secondary rotation {np.round(np.degrees(secondary_rotation_angle), 2)}° around {rotation_axis[1]}-axis applied")

            # Generate primary rotation matrix
            R_p, required_angle, new_plane = primary_rotation_handling(sequence_ID, new_plane, all_positions[idx + 1],
                                                                       primary_angle, rotation_axis)
            primary_angle = required_angle

            logging.debug(f"Primary matrix: \n{np.round(R_p, 2)} \n")

        else:

            logging.debug(f"Step {idx}: Same meridian")

            # Create copy of previous plane and translate it to new position
            new_plane = initialise_new_circle(rotated_planes[idx - 1], position)
            new_plane.title = f"Plane {idx}"

            logging.debug(f"Plane {idx} initial direction: {np.round(new_plane.direction, 2)}")

            # Apply rotation
            new_plane.rotate_plane(R_p)
            logging.debug(f"Plane {idx}: Applying primary rotation {np.round(np.degrees(primary_angle), 2)}°")
            logging.debug(f"Plane {idx} rotated direction: {np.round(new_plane.direction, 2)}")

        # Append new plane from ANY above ^^^^
        rotated_planes.append(new_plane)

        new_plane.print_pose()

    return rotated_planes


def visualise_intersections(fig, lines):
    """
    Checks intersection results, and adds to plot to indicate results - hits and misses in green and red.

    Args:
        fig: The graphic object to update.
        lines: List of Line objects.

    Returns:
        Updated Plotly figure
    """
    for line in lines:
        if line.result == 1:  # Hit
            fig = line.plot_lines_3d(fig, "green")
        else:  # Miss
            fig = line.plot_lines_3d(fig, "red")

    return fig


def visualise_intersections_seq(line):
    """
    Checks intersection results, and adds to plot to indicate results - hits and misses in green and red.

    Args:
        line: List of Line objects.

    Returns:
        Updated Plotly figure
    """

    if line.result == 1:
        color = 'green'
    else:
        color = 'red'

    x = [line.position[0], line.intersection_coordinates[0]]
    y = [line.position[1], line.intersection_coordinates[1]]
    z = [line.position[2], line.intersection_coordinates[2]]

    scatter_obj = go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        showlegend=False,
        line={'color': color, 'width': 3}
    )

    return scatter_obj


def check_fig_data(fig):
    logging.debug("\n")
    logging.debug(f"Number of traces: {len(fig.data)}")
    for idx, trace in enumerate(fig.data):
        logging.debug(
            f"Trace {idx}: Type = {type(trace)}, Name = {trace.name if hasattr(trace, 'name') else 'Unnamed'}")


def prepare_line_samples(lines, line_list, sample_size):
    """
    Samples list of lines for visualisation
    Returns graphic objects of random lines

    :arg:
        lines: List of Line objects
        line_list: line_id list
        sample_size: Number of lines to be selected
    :return:
    """

    # exit(2)

    lines_graphics = []
    # Validate sample size

    if line_list is None or len(line_list) == 0:
        logging.debug("No lines to sample.")
        return None

    logging.debug(f"Sample size: {sample_size}")
    logging.debug(f"Number of lines: {len(line_list)}")

    if sample_size > len(line_list):
        logging.warning(f"Sample size {sample_size} is larger than number of lines {len(line_list)}.")
        sample_size = len(line_list)

    # Extract samples
    sampled_lines = random.sample(line_list, sample_size)

    for samples in sampled_lines:
        lines_graphics.append(visualise_intersections_seq(lines[samples]))  # Stores line objects

    logging.debug(f"Returning {len(lines_graphics)} lines for visualisation.")
    return lines_graphics


def rigid_arc_rotation(radius, arc_resolution_deg, tilt_angles):
    """
    Generates 3D coordinates along a semicircular arc in the x-z plane,
    then applies a series of rotations about the x-axis using the provided tilt angles.

    Args:
        radius (float): Radius of the arc.
        arc_resolution_deg (float): Angle increment for arc sampling.
        tilt_angles (list or array): List of angles to rotate arc about x-axis.

    Returns:
        np.ndarray: Stacked array of all rotated arc positions in Cartesian coordinates (shape: [N_total, 3])
    """
    # Generate arc angles from 0 to 180 degrees (semi-circle)
    theta_arc = np.radians(np.arange(0, 180 + arc_resolution_deg, arc_resolution_deg))

    # Arc in x-z plane
    x = radius * np.cos(theta_arc)
    y = np.zeros_like(x)
    z = radius * np.sin(theta_arc)

    arc_points = np.vstack((x, y, z))  # shape: [3, N]

    all_rotated_positions = []

    for tilt_angle_deg in tilt_angles:
        # Rotation matrix about x-axis
        tilt_rad = np.radians(tilt_angle_deg)
        R_x = np.array([
            [1, 0, 0],
            [0, np.cos(tilt_rad), -np.sin(tilt_rad)],
            [0, np.sin(tilt_rad), np.cos(tilt_rad)]
        ])

        # Apply rotation
        rotated_arc = R_x @ arc_points  # shape: [3, N]
        all_rotated_positions.append(rotated_arc.T)  # shape: [N, 3]

        logging.debug(f"Rotated arc size: {np.shape(rotated_arc.T)}")

        logging.debug(f"Rotated arc: {np.shape(all_rotated_positions)}")

    return np.vstack(all_rotated_positions)  # shape: [N_total, 3]


def log_parameters(primary_angle, secondary_angle, rotation_step, rotation_axis, sequence_ID):
    # Display simulation parameters
    logging.debug(f"sequence ID: {sequence_ID}")
    logging.debug(f"Primary angle: {primary_angle}")
    logging.debug(f"Secondary angle: {secondary_angle}")
    logging.debug(f"Rotation step: {np.round(np.degrees(rotation_step), 2)}")
    logging.debug(f"Rotation axis: {rotation_axis}")


def get_horizontal_params(config):
    """
    Returns the parameters required to set up horizontal circle style of movements
    Returns:
    """
    logging.info("Horizontal circles movement")

    # Phi goes from 90 down to input arc_phi step
    arc_phi_angle = np.arange(
        90,
        -config.arc_movement["horizontal_secondary"],
        -config.arc_movement["horizontal_secondary"])  # Secondary rotation (between meridians)

    arc_theta_angle = config.arc_movement["horizontal_primary"]  # Primary rotation (rotate on same meridian)

    sequence_ID = 2  # 2 for horizontal circles movement

    rotation_axis = ["z", "y"]
    rotation_step = np.radians(arc_theta_angle)  # Primary rotation (rotate on same meridian)

    log_parameters(arc_theta_angle, config.arc_movement["horizontal_secondary"], rotation_step, rotation_axis,
                   sequence_ID)

    return arc_phi_angle, arc_theta_angle, sequence_ID, rotation_axis, rotation_step


def get_vertical_params(config):
    """
    Returns the parameters for vertical circle movement.
    """
    logging.info("Vertical circles movement")

    arc_phi_angle = config.arc_movement["vertical_primary"]  # Primary rotation (rotate on same meridian)
    arc_theta_angle = config.arc_movement["vertical_secondary"]  # Secondary rotation (rotate between meridians)

    sequence_ID = 1  # 1 for vertical circles movement

    rotation_axis = ["y", "z"]
    rotation_step = np.radians(-arc_phi_angle)  # Primary rotation (rotate on same meridian)

    log_parameters(arc_phi_angle, arc_theta_angle, rotation_step, rotation_axis, sequence_ID)

    return arc_phi_angle, arc_theta_angle, sequence_ID, rotation_axis, rotation_step


def get_rigid_params(config):
    """
    Returns the parameters for rigid arc movement.
    Also, directly computes the 'rigid_arc_positions' array.
    """
    logging.info("Rigid Arc circles movement")

    rigid_arc_step = config.arc_movement["rigid_arc_step"]

    tilt_angles = config.arc_movement["tilt_angles"]

    sequence_ID = 3  # 3 for rigid arc movement

    rotation_axis = ["y", "z"]
    rotation_step = np.radians(-10)

    # Generate positions for rotation in rigid arc
    rigid_arc_positions = rigid_arc_rotation(config.arc_movement["radius"], rigid_arc_step, tilt_angles)

    logging.debug(f"Rigid arc positions shape: {np.shape(rigid_arc_positions)}")

    return rigid_arc_step, tilt_angles, sequence_ID, rotation_axis, rotation_step, rigid_arc_positions


@profile(stream=open("memory_profile.log", "w"))
def main():
    """
    Runs the main program
        1. Initialises planes and areas.
        2. Creates lines from the source plane.
        3. Sets up a 3D plot and visualises the environment, including planes and areas.
        4. Applies rotation to the source plane and updates the visualization.
        5. Rotates the lines according to the transformed source plane.
        6. Evaluates intersections between lines and the sensor plane, visualises results, and calculates hit/miss information.
        7. Displays the final 3D plot and prints the hit/miss results.
    """
    # ----- Step 1: Initialize planes and areas  ----- #
    sensorPlane, sourcePlane, aperturePlane, sensorAreas, aperture_areas = initialise_planes_and_areas()

    # ----- Step 2: Create lines from source plane ----- #
    lines = create_lines_from_plane(sourcePlane, config.simulation["num_lines"])

    # ----- Step 3: Create 3D plot and visualize environment ----- #
    fig = initialise_3d_plot(sensorPlane)  # Applies plot formatting and global axes

    # Apply visualization settings from config
    if config.visualization["show_sensor_plane"]:
        fig = visualise_environment(fig, sensorPlane, config.visualization["color_sensor_plane"])
    if config.visualization["show_source_plane"]:
        fig = visualise_environment(fig, sourcePlane, config.visualization["color_source_plane"])
    if config.visualization["show_aperture_plane"]:
        fig = visualise_environment(fig, aperturePlane, config.visualization["color_aperture_plane"])
    if config.visualization["show_sensor_area"]:
        for sensor in sensorAreas:  # Display all defined sensors on the plot
            fig = visualise_environment(fig, sensor, config.visualization["color_sensor_area"])
    if config.visualization["show_aperture_area"]:
        for aperture in aperture_areas:  # Display all defined apertures on the plot
            fig = visualise_environment(fig, aperture, config.visualization["color_aperture_area"])

    with open("results.csv", "w") as results_file:
        results_file.write(f"idx, hits, misses\n")

    sensorPlane.title = "Parent axis"
    sensorPlane.print_pose()

    sourcePlane.title = "Source plane"
    sourcePlane.print_pose()

    #        ----- Step 4: Arc movements -----        #
    # -- Phase 1: Compute arc steps -- #
    # Set identify which type of movement
    # Prepare position P vectors throughout movement

    # Movement style booleans
    horizontal_circles = config.arc_movement["horizontal_circles"]
    vertical_circles = config.arc_movement["vertical_circles"]
    rigid_arc = config.arc_movement["rigid_arc"]

    #Initialise variables
    arc_phi_angle = None
    arc_theta_angle = None
    sequence_id = None
    rotation_axis = None
    rotation_step = 0.0
    rigid_positions = None

    # Read from JSON config, set up for style of movement
    if horizontal_circles:
        (arc_phi_angle,
         arc_theta_angle,
         sequence_ID,
         rotation_axis,
         rotation_step) = get_horizontal_params(config)

        # Generate movement sequence
        all_positions, secondary_movement = rotation_rings(
            sequence_ID,
            config.arc_movement["radius"],  # Radius of arc movement
            arc_theta_angle,  # steps of theta taken around the arc
            arc_phi_angle  # phi levels to the spherical arc
        )
        # Correct form of secondary movement for horizontal circles
        reference_angle = secondary_movement[0]
        secondary_movement -= reference_angle  # sets the secondary angle to the starting position (not abs)

    elif vertical_circles:
        (arc_phi_angle,
         arc_theta_angle,
         sequence_ID,
         rotation_axis,
         rotation_step) = get_vertical_params(config)

        # Generate movement sequence
        all_positions, secondary_movement = rotation_rings(
            sequence_ID,
            config.arc_movement["radius"],  # Radius of arc movement
            arc_theta_angle,  # steps of theta taken around the arc
            arc_phi_angle  # phi levels to the spherical arc
        )

    elif rigid_arc:
        (arc_phi_angle,
         arc_theta_angle,
         sequence_ID,
         rotation_axis,
         rotation_step,
         all_positions) = get_rigid_params(config)

        secondary_movement = np.zeros(len(all_positions))  # not needed

    else:
        logging.warning("No movement")
        exit(3)

    # -- Phase 2: Move to first arc position -- #
    start_pose_plane = setup_initial_pose(
        sourcePlane,
        config.arc_movement["initial_rotation"],
        config.arc_movement["rotation_axis"],
        all_positions
    )

    # -- Phase 3: Apply the plane along the arc -- #
    # Move plane along arc and update lines
    if config.arc_movement["execute_movements"]:
        rotated_planes = move_plane_along_arc(
            start_pose_plane,
            all_positions,
            rotation_step,
            rotation_axis,
            secondary_movement,
            sequence_ID
        )
    else:
        rotated_planes = [start_pose_plane]

    # #        ----- Step 6: Evaluate hits and visualize lines -----        #
    logging.info(f"\n\nChecking intersections:\n")
    # check_fig_data(fig)
    line_scatter_objects = []
    results = np.zeros((len(rotated_planes), 2))

    for idx, plane in enumerate(rotated_planes):  # Check lines for each plane
        update_lines_global_positions(lines, plane)
        logging.info(f"{plane.title}")
        hit, miss, hit_list, miss_list = evaluate_line_results(sensorPlane, sensorAreas, aperturePlane, aperture_areas,
                                                               lines)
        handle_results(sensorAreas)
        logging.debug(f"{plane.title} has {hit} hits and {miss} misses")

        results[idx, 0] = hit
        results[idx, 1] = miss

        with open("results.csv", "a") as results_file:
            results_file.write(f"{idx}, {results[idx, 0]}, {results[idx, 1]}\n")

        # Sample lines for visualisation
        logging.debug(f"Selecting hits for visualisation for plane {idx}")
        lines_for_plane = []

        hits_visualised = (prepare_line_samples(lines, hit_list, config.visualization["hits_to_display"]))

        if hits_visualised is not None:
            lines_for_plane.extend(hits_visualised)

        logging.debug(f"Selecting misses for visualisation for plane {idx}")
        misses_visualised = (prepare_line_samples(lines, miss_list, config.visualization["misses_to_display"]))

        if misses_visualised is not None:
            lines_for_plane.extend(misses_visualised)

        # Stores line objects for all planes
        line_scatter_objects.append(lines_for_plane)
        logging.debug(f"Line scatter objects: {type(line_scatter_objects)} length {len(line_scatter_objects)}")

    #        ----- Step 7: Display the plot and results -----        #
    # Show any plot
    if config.visualization["show_output_parent"]:

        # show animation or static plot
        if config.visualization["animated_plot"]:
            fig = generate_arc_animation(fig, rotated_planes, line_scatter_objects, results)
            logging.info("Animated plot generated.")
        else:
            fig = generate_static_arc_plot(fig, rotated_planes, line_scatter_objects)
            logging.info("Static plot generated.")

        fig.show()
    else:
        logging.info("Visualization disabled (show_output_parent = false).")

    print("\nFinished.    \n")


if __name__ == "__main__":
    main()
