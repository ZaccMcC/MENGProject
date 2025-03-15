from arcRotation import arc_movement_vector, rotation_rings
from intersectionCalculations import intersection_wrapper  # Import for calculating line-plane intersection
from line import Line  # Import for Line object
from plane import Plane  # Import for Plane object
from areas import Areas  # Import for target areas
import numpy as np  # For mathematical operations
import plotly.graph_objects as go  # For 3D visualization

from memory_profiler import profile

import logging
from config import config

# Valid logging levels "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"


def initialise_planes_and_areas():
    """
Initialises all planes and the target area.
Returns: sensorPlane, sourcePlane, interPlane, and sensorArea
"""

    # Define the source plane
    # Defines its position (centre point), its direction (facing down)
    sourcePlane = Plane("Source Plane", **config.planes["source_plane"])

    # Define the sensor plane
    sensorPlane = Plane("Sensor Plane", **config.planes["sensor_plane"])

    # Define the intermediate plane
    interPlane = Plane("Inter-plane", **config.planes["intermediate_plane"])

    # Define the sensor area (target area on the sensor plane)
    sensorArea = Areas("Sensor Area", **config.sensor_area)

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


def visualise_environment(fig, planeObject, colour):  # sensorPlane, sourcePlane, interPlane, sensorArea):
    """
    Adds planes and areas to the 3D plot for visualization.
    Returns: Updated Plotly figure.
    """
    fig = planeObject.planes_plot_3d(fig, colour)
    return fig


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

    lines = [Line([x, y, 0], source_plane.direction)
             for x, y in local_positions]

    # Initialize their global positions based on the plane
    for line in lines:
        line.update_global_position(source_plane)

    return lines


def evaluate_line_results(sensorPlane, sensorArea, lines):
    """
    Checks intersections of lines with the sensor plane and evaluates whether they hit the target area.

    Updates line object internal parameters with the results.

    Args:
        sensorPlane: The plane intersecting with the lines.
        sensorArea: The target area to evaluate hits.
        lines: List of Line objects.

    Returns:
        hit: number of hits.
        miss: number of misses.
    """
    hit = 0
    miss = 0

    for line in lines:
        # Calculate intersection between the line and the sensor plane
        intersection_coordinates = intersection_wrapper(sensorPlane, line)

        # Check if the intersection point is in the target area
        result = sensorArea.record_result(intersection_coordinates)

        if result == 1:  # Hit
            line.result = 1
            hit += 1
        elif result == 0:  # Miss
            line.result = 0
            miss += 1

        line.intersection_coordinates = intersection_coordinates


    print(f"Total number of hits recorded: {hit}")
    print(f"Total number of misses recorded: {miss}")

    return hit, miss


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
    print(f"Moving to initial arc position: {all_positions[0]}")
    start_pose_plane.position = np.array(all_positions[0])
    start_pose_plane.title = "Plane moved to initial arc position"
    start_pose_plane.print_pose()

    return start_pose_plane


def generate_arc_animation(fig, rotated_planes, static_traces):
    """
    Generates an animated visualization of the arc movement.

    Args:
        fig (Plotly Figure): The figure used for visualization.
        rotated_planes (list): The list of planes from move_plane_along_arc().
        static_traces (list): Static objects to keep in the visualization.

    Returns:
        fig (Plotly Figure): Updated figure with animation.
    """

    frames = []

    for idx, plane in enumerate(rotated_planes):
        # Debugging - Check if planes are being added
        logging.debug(f"Adding frame {idx} for plane at position {plane.position}")

        # Get plane and axis traces
        plane_trace = plane.planes_plot_3d(go.Figure(), "yellow").data[0]
        axis_traces = plane.plot_axis(go.Figure()).data  # Should return all 3 axes

        # If axis_traces is empty, warn in logs
        if len(axis_traces) < 3:
            logging.warning(f"Step {idx}: Not all axis traces were generated!")

        # Create animation frame
        frame = go.Frame(
            data=[plane_trace] + list(axis_traces) + list(static_traces),
            name=f"Step {idx}"
        )
        frames.append(frame)

    # Ensure frames are actually created
    if not frames:
        logging.error("No frames were generated for animation!")

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
                    "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
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
        }]
    )

    fig.frames = frames
    return fig


def generate_static_arc_plot(fig, rotated_planes):
    """
    Generates a static 3D plot of all plane positions in the arc.

    Args:
        fig (Plotly Figure): The figure used for visualization.
        rotated_planes (list): The list of planes from move_plane_along_arc().

    Returns:
        fig (Plotly Figure): Updated figure with static planes plotted.
    """

    for idx, plane in enumerate(rotated_planes):
        if idx == 0:
            fig = plane.planes_plot_3d(fig, "green")
        else:
            fig = plane.planes_plot_3d(fig, "blue")

        fig = plane.plot_axis(fig)  # Adds axis vectors

    return fig


def move_plane_along_arc(plane, all_positions, arc_angle, rotation_axis, polar_positions):
    """
    Moves the plane along a predefined arc while updating line positions.

    Args:
        plane (Plane): Plane in starting position.
        all_positions (list): Position vectors along the arc.
        arc_angle (float): Rotation angle per step.
        rotation_axis (str): Axis of rotation.
        polar_positions (list): Polar coordinates for reference.

    Returns:
        rotated_planes (list): Transformed plane objects at each step.
        fig (Plotly figure): Updated visualization.
    """

    rotated_planes = []

    initial_phi = polar_positions[0][2]  # Store initial phi angle

    for idx, position in enumerate(all_positions):
        # Copy last plane position
        if idx == 0:
            new_plane = Plane(f"Step {idx}", plane.position, plane.direction, plane.width, plane.length)
            new_plane.right, new_plane.up, new_plane.direction = plane.right, plane.up, plane.direction

            rotated_planes.append(new_plane)
            continue
        else:
            new_plane = Plane(f"Step {idx}", rotated_planes[idx - 1].position,
                              rotated_planes[idx - 1].direction, rotated_planes[idx - 1].width,
                              rotated_planes[idx - 1].length)
            # Overwrite newly generated local axes, preserving previous
            new_plane.right, new_plane.up, new_plane.direction = rotated_planes[idx - 1].right, rotated_planes[idx - 1].up, rotated_planes[idx - 1].direction

        # Compute transformation
        translation_vector = arc_movement_vector(new_plane, position)
        rotation_matrix = do_rotation(np.radians(arc_angle), "z")

        logging.debug(f"Beginning of arc movement {idx}")
        logging.debug(f"Current Position: [{new_plane.position[0]:.2f}, {new_plane.position[1]:.2f}, {new_plane.position[2]:.2f}]")
        logging.debug(f"Next Position: [{position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}]\n")


        # Apply transformations

        # Apply rotation to align with the origin in the z axis
        logging.info(f"Rotating {arc_angle}° around z-axis")
        new_plane.rotate_plane(rotation_matrix)

        # Check if next step requires additional rotation
        if polar_positions[idx][2] != initial_phi:
            logging.debug(f"Applying phi rotation")
            correction_angle = initial_phi - polar_positions[idx][2]
            new_plane.rotate_plane(do_rotation(-correction_angle, "y"))
            initial_phi = polar_positions[idx][2]

        # Apply rotation
        new_plane.translate_plane(translation_vector)
        rotated_planes.append(new_plane)

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
    sensorPlane, sourcePlane, interPlane, sensorArea = initialise_planes_and_areas()

    # ----- Step 2: Create lines from source plane ----- #
    lines = create_lines_from_plane(sourcePlane, 60)

    # ----- Step 3: Create 3D plot and visualize environment ----- #
    fig = initialise_3d_plot(sensorPlane) # Applies plot formatting and global axes

    # Apply visualization settings from config
    if config.visualization["show_sensor_plane"]:
        fig = visualise_environment(fig, sensorPlane, config.visualization["color_sensor_plane"])
    if config.visualization["show_source_plane"]:
        fig = visualise_environment(fig, sourcePlane, config.visualization["color_source_plane"])
    if config.visualization["show_intermediate_plane"]:
        fig = visualise_environment(fig, interPlane, config.visualization["color_intermediate_plane"])
    if config.visualization["show_sensor_area"]:
        fig = visualise_environment(fig, sensorArea, config.visualization["color_sensor_area"])

    sensorPlane.title = "Parent axis"
    sensorPlane.print_pose()

    sourcePlane.plot_axis(fig)

    sourcePlane.title = "Source plane"
    sourcePlane.print_pose()

    # #        ----- Step 4: Arc movements -----        #
    # # -- Phase 1: Compute arc steps -- #
    # # Gets all position P vectors for the plane as it rotates around arc
    # # Increments first through arc_theta_angles, then phis
    # arc_phi_angle = np.arange(90, -config.arc_movement["arc_phi_step"], -config.arc_movement["arc_phi_step"])
    #
    # all_positions, all_positions_polar = rotation_rings(
    #     arc_phi_angle, # phi levels to the spherical arc
    #     config.arc_movement["radius"],# Radius of arc movement
    #     config.arc_movement["arc_theta_angle"] # steps of theta taken around the arc
    # )
    #
    # # -- Phase 2: Move to first arc position -- #
    # start_pose_plane = setup_initial_pose(
    #     sourcePlane,
    #     config.arc_movement["initial_rotation"],
    #     config.arc_movement["rotation_axis"],
    #     all_positions
    # )
    #
    # # -- Phase 3: Apply the plane along the arc -- #
    # # Move plane along arc and update lines
    # rotated_planes = move_plane_along_arc(
    #     start_pose_plane,
    #     all_positions,
    #     config.arc_movement["arc_theta_angle"],
    #     "z",
    #     all_positions_polar,
    # )


    #        ----- Step 6: Evaluate hits and visualize lines -----        #
    hit, miss = evaluate_line_results(sensorPlane, sensorArea, lines)
    visualise_intersections(fig, lines)


    fig.show()
    exit(2)
    #        ----- Step 7: Display the plot and results -----        #
    try:
        if config.visualization["show_output_parent"]:
            # Determine if we show animation or static plot
            if config.visualization["animated_plot"]:
                fig = generate_arc_animation(fig, rotated_planes, fig.data)
            else:
                fig = generate_static_arc_plot(fig, rotated_planes)
                logging.info("Static plot generated.")

            fig.show()
        else:
            print("Visualization disabled (show_output_parent = false).")

        print("\n   Finished.    \n")

    except Exception as e:
        print(f"Plotly Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
