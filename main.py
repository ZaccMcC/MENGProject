from arcRotation import arc_movement_coordinates, arc_movement_vector
from intersectionCalculations import intersection_wrapper  # Import for calculating line-plane intersection
from line import Line  # Import for Line object
from plane import Plane, compute_local_axes  # Import for Plane object
from areas import Areas  # Import for target areas
import numpy as np  # For mathematical operations
import plotly.graph_objects as go  # For 3D visualization

import logging


# from rotationTest import sourcePlane


def initialise_planes_and_areas():
    """
Initialises all planes and the target area.
Returns: sensorPlane, sourcePlane, interPlane, and sensorArea
"""

    # Define the source plane
    source_plane_position = ([0, 0, 1])
    source_plane_direction = ([0, 0, -1])
    sourcePlane = Plane("Source Plane", source_plane_position, source_plane_direction, 10, 10)

    # Define the sensor plane
    sensor_plane_position = ([0, 0, 0])  # Defines its position (centre point)
    sensor_plane_direction = ([0, 0, 1])  # Defines its direction (facing down)
    sensorPlane = Plane("Sensor Plane", sensor_plane_position, sensor_plane_direction, 10, 10)

    # Define the intermediate plane
    inter_plane_position = ([0, 0, 1])
    inter_plane_direction = ([0, 0, 1])
    interPlane = Plane("Inter-plane", inter_plane_position, inter_plane_direction, 5, 5)

    # Define the sensor area (target area on the sensor plane)
    sensor_area_position = ([4, 3, 0])
    sensor_area_direction = ([0, 0, 1])
    sensorArea = Areas("Sensor", sensor_area_position, sensor_area_direction, 2, 2)

    return sensorPlane, sourcePlane, interPlane, sensorArea


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
        title="3D Planes and Lines Visualization"

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


def visualise_environment(fig, planeObject, colour):  # sensorPlane, sourcePlane, interPlane, sensorArea):
    """
    Adds planes and areas to the 3D plot for visualisation.
    Returns: Updated Plotly figure.
    """
    fig = planeObject.planes_plot_3d(fig, colour)
    return fig


def create_lines_from_random_points(sourcePlane, num_points, direction):
    """
    Randomly generates points on the source plane and creates lines originating
    from those points.

    Args:
        sourcePlane: The plane on which random points will be generated.
        num_points: Number of random points to generate.
        direction: Direction vector for the lines.

    Returns:
        A list of Line objects.
    """
    randomPoints = sourcePlane.random_points(num_points)
    lines = [
        Line((point[0], point[1], sourcePlane.position[2]), direction) for point in randomPoints]
    return lines


def evaluate_hits_and_visualize(fig, sensorPlane, sensorArea, lines):
    """
    Checks intersections of lines with the sensor plane and evaluates
    whether they hit the target area.
    Visualizes hits in green and misses in red.

    Args:
        fig: The 3D Plotly figure for visualization.
        sensorPlane: The plane intersecting with the lines.
        sensorArea: The target area to evaluate hits.
        lines: List of Line objects.

    Returns:
        Updated Plotly figure, number of hits, number of misses.
    """
    hit = 0
    miss = 0

    for line in lines:
        # Calculate intersection between the line and the sensor plane
        intersection_coordinates = intersection_wrapper(sensorPlane, line)

        # Check if the intersection point is in the target area
        result = sensorArea.record_result(intersection_coordinates)

        if result == 1:  # Hit
            fig = line.plot_lines_3d(fig, intersection_coordinates, "green")
            hit += 1
        elif result == 0:  # Miss
            fig = line.plot_lines_3d(fig, intersection_coordinates, "red")
            miss += 1

    print(f"Total number of hits recorded: {hit}")
    print(f"Total number of misses recorded: {miss}")

    return fig, hit, miss


def do_rotation(theta, axis):
    """
    Gets rotation matrix for specified axis and angle.

    Args:
        theta: The angle of rotation in degrees (converted to radians later).
        axis: The axis of rotation.

    Returns:
        The rotation matrix for the specified axis and angle.
    """

    # theta = np.radians(degrees)
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
    start_pose_plane.position = np.array(all_positions[0])
    start_pose_plane.title = "Plane moved to initial arc position"
    start_pose_plane.print_pose()

    return start_pose_plane


def move_plane_along_arc(fig, plane, all_positions, arc_angle, rotation_axis):
    """
    Moves the plane along a predefined arc by applying rotation and translation at each step.
    Uses logging for debugging

    Args:
        fig (Plotly): The display figure used for visualisation.
        plane (object): Plane in starting position which will be moved around arc.
        all_positions (list): Contains all position vectors around the arc.
        rotation_axis (str): The axis of rotation used to keep normal pointing towards global origin.

    Returns:
        rotated_planes: Array of transformed planes at each position around the arc.
    """

    rotated_planes = []

    for idx, positions in enumerate(all_positions):
        # Create copies of the plane for each new position around the arc
        if idx == 0:  # If plane is in 'start' position of the arc
            rotated_planes.append(Plane(f"Plane in position {idx} of arc movement",
                                        plane.position,
                                        plane.direction,
                                        plane.width,
                                        plane.length))
            print("Starting position")
            fig = visualise_environment(fig, rotated_planes[idx], "green")
            plane.plot_axis(fig)
            continue

        else:  # If plane has already started arc
            rotated_planes.append(Plane(f"Plane in position {idx} of arc movement",
                                        rotated_planes[idx - 1].position,
                                        rotated_planes[idx - 1].direction,
                                        rotated_planes[idx - 1].width,
                                        rotated_planes[idx - 1].length))

        currentPosition = rotated_planes[idx].position
        nextPosition = positions

        logging.debug(f"Beginning of arc movement {idx}")
        logging.debug(f"Current Position: [{currentPosition[0]:.2f}, {currentPosition[1]:.2f}, {currentPosition[2]:.2f}]")
        logging.debug(f"Next Position: [{nextPosition[0]:.2f}, {nextPosition[1]:.2f}, {nextPosition[2]:.2f}]")

        # Get vector required to move plane between current position
        new_vector = arc_movement_vector(rotated_planes[idx], positions)
        logging.debug(f"Translation vector: [{new_vector[0]:.2f}, {new_vector[1]:.2f}, {new_vector[2]:.2f}]")

        # Apply rotation
        logging.info(f"Rotating {arc_angle}° around {rotation_axis}-axis")
        rotated_planes[idx].rotate_plane(do_rotation(np.radians(arc_angle), "z"))

        # Apply translation
        rotated_planes[idx].translate_plane(new_vector)

        # Plot results
        fig = visualise_environment(fig, rotated_planes[idx], "blue")
        rotated_planes[idx].print_pose()
        rotated_planes[idx].plot_axis(fig)

    return rotated_planes, fig


def main():
    """
    Runs the main program
        1. Initialises planes and areas.
        2. Creates lines from the source plane.
        3. Sets up a 3D plot and visualises the environment, including planes and areas.
        4. Applies rotation to the source plane and updates the visualisation.
        5. Rotates the lines according to the transformed source plane.
        6. Evaluates intersections between lines and the sensor plane, visualises results, and calculates hit/miss information.
        7. Displays the final 3D plot and prints the hit/miss results.
    """
    # ----- Step 1: Initialize planes and areas  ----- #
    sensorPlane, sourcePlane, interPlane, sensorArea = initialise_planes_and_areas()

    # ----- Step 2: Create lines from source plane ----- #
    lines = create_lines_from_random_points(sourcePlane, num_points=60, direction=sourcePlane.direction)

    # ----- Step 3: Create 3D plot and visualize environment ----- #
    fig = initialise_3d_plot(sensorPlane)
    fig = visualise_environment(fig, sensorPlane, "red")
    fig = visualise_environment(fig, sourcePlane, "yellow")
    # fig = visualise_environment(fig, interPlane, "green")
    # fig = visualise_environment(fig, sensorArea, "#00FF00")

    sensorPlane.title = "Parent axis"
    sensorPlane.print_pose()

    sourcePlane.plot_axis(fig)

    #        ----- Step 4: Arc movements -----        #
    # -- Phase 1: Initialise arc parameters -- #
    radius = 9  # Radius position for arc movement
    theta = 90  # Degrees of rotation for normal vector correction
    rotation_axis = "y"  # Rotate y-axis for correct normal vector at arc starting
    arc_angle = 90  # Degrees of rotation

    # -- Phase 2: Compute arc steps -- #
    all_positions, allPositions_polar = arc_movement_coordinates(radius, arc_angle)

    # Move to first arc position
    start_pose_plane = setup_initial_pose(sourcePlane, theta, rotation_axis, all_positions)

    # -- Phase 3: Move the plane along the arc -- #
    new_planes, _ = move_plane_along_arc(fig, start_pose_plane, all_positions, arc_angle, rotation_axis)

    #        ----- Step 5: Rotate lines -----        #
    # for i in lines:
    #     i.update_position(new_planes[0])

    #        ----- Step 6: Evaluate hits and visualize lines -----        #
    # fig, hit, miss = evaluate_hits_and_visualize(fig, sensorPlane, sensorArea, lines)

    #        ----- Step 7: Display the plot and results -----        #
    try:
        fig.show()
        print("\n   🚨    \n")
    except Exception as e:
        print(f"Plotly Error: {e}")
        exit(1)

    # start_pose_plane.print_pose()


if __name__ == "__main__":
    main()
