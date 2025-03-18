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
        logging.debug(f"Checking intersection with {target.title}...")

        if result == 1: # Hit occurs
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
        lines: List of Line objects.

    Returns:
        hit: number of hits.
        miss: number of misses.
    """
    hit = 0
    miss = 0
    result = None

    # Reset previous sensor illumination values
    for sensors in sensorArea:
        sensors.illumination = 0

    for line in lines:
        line.result = 0
        # Calculate intersection between the line and the aperture plane
        aperture_intersection_coordinates = intersection_wrapper(aperturePlane, line)
        # Set intersection coordinate of line object
        line.intersection_coordinates = aperture_intersection_coordinates

        logging.debug(f"Checking line {line.line_id} intersection with apertures...")
        # Check if intersection with apertures
        aperture_intersection, _ = intersection_checking(apertureAreas, aperture_intersection_coordinates)
        if aperture_intersection == 1: # Hit, at apertures
            logging.debug(f"Line {line.line_id} hit apertures")
            # Get intersection coordinates with sensor plane
            sensor_intersection_coordinates = intersection_wrapper(sensorPlane, line)
            # Check intersection with sensor areas
            sensor_intersection, sensor = intersection_checking(sensorArea, sensor_intersection_coordinates)
            line.intersection_coordinates = sensor_intersection_coordinates
            if sensor_intersection == 1: # Intersection occurs at sensor
                hit, line.result, sensor.illumination = hit + 1, 1, sensor.illumination + 1

                # logging.debug(f"Line {line.line_id} hit {sensor.title}")
                continue  # Move to next line
            if sensor_intersection == 0:
                miss += 1
                continue
        else:
            logging.debug(f"Line {line.line_id} missed apertures")
            miss += 1
            continue

    return hit, miss


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
        plane_trace.append(plane.planes_plot_3d(go.Figure(), "yellow").data[0])  # makes plane_trace[idx] type = "plotly.graph_objs._mesh3d.Mesh3d"
        axis_traces.append(list(plane.plot_axis(go.Figure()).data))  # makes axis_traces[idx] type = "tuple"

        frame_titles[idx] = f"Position {idx} - Hits {results[idx][0]:.0f}, Misses {results[idx][1]:.0f} "

    # print("")
    # # Debug messages
    # debug_params = [plane_trace, axis_traces, lines_traces]
    # params_str = "plane_trace", "axis_traces", "lines_traces"
    # for i, param in enumerate(debug_params):
    #     logging.debug(f"Param {params_str[i]} type: {type(param)}: shape {np.shape(param)}")
    #     logging.debug(f"Param {params_str[i]} [0] type: {type(param[0])}: shape {np.shape(param[0])}")

    check_fig_data(fig)

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

        logging.debug(f"Adding line traces for plane {idx}")
        for line in line_objects[idx]:
            fig.add_trace(line)

    return fig


def move_plane_along_arc(plane, all_positions, arc_angle, rotation_axis, secondary_axis, sequence_ID):
    """
    Moves the plane along a predefined arc while updating line positions.

    Args:
        plane (Plane): Plane in starting position.
        all_positions (list): Position vectors along the arc.
        arc_angle (float): Rotation angle per step in radians.
        rotation_axis (list): Axis of rotation.
        secondary_axis (list): Polar coordinates for reference.
        sequence_ID (int): Indicates type of movement sequence. (1 or 2)

    Returns:
        rotated_planes (list): Transformed plane objects at each step.
        fig (Plotly figure): Updated visualization.
    """

    rotated_planes = []
    current_secondary = secondary_axis[0]  # Store initial secondary axis angle
    meridian_start_index = 0  # Track where each meridian starts

    for idx, position in enumerate(all_positions):
        # Copy last plane position
        if idx == 0:
            new_plane = Plane(f"Step {idx}", plane.position, plane.direction, plane.width, plane.length)
            new_plane.right, new_plane.up, new_plane.direction = plane.right, plane.up, plane.direction

            rotated_planes.append(new_plane)
            continue
        else:
            # Check if starting a new meridian (for vertical circles)
            if sequence_ID == 1 and idx > 0 and secondary_axis[idx] != secondary_axis[idx-1]:
                # Start a new meridian from a fresh orientation
                meridian_start_index = idx
                # Clone the original plane for a fresh start
                new_plane = Plane(f"Step {idx}", plane.position, plane.direction, plane.width, plane.length)
                new_plane.right, new_plane.up, new_plane.direction = plane.right, plane.up, plane.direction

                # Apply initial setup for this meridian
                # 1. Rotate around z-axis to the correct theta angle
                theta_rotation = secondary_axis[idx]  # This should be the theta value for this meridian

                new_plane.rotate_plane(do_rotation(theta_rotation, "z"))

                # 2. Translate to the start position for this meridian
                translation_vector = arc_movement_vector(new_plane, position)
                new_plane.translate_plane(translation_vector)
            else:
                new_plane = Plane(f"Step {idx}", rotated_planes[idx - 1].position,
                                  rotated_planes[idx - 1].direction, rotated_planes[idx - 1].width,
                                  rotated_planes[idx - 1].length)

                # Overwrite newly generated local axes, preserving previous
                new_plane.right, new_plane.up, new_plane.direction = rotated_planes[idx - 1].right, rotated_planes[
                    idx - 1].up, rotated_planes[idx - 1].direction

                logging.debug(f"Beginning of arc movement {idx}")

                # Compute translation
                translation_vector = arc_movement_vector(new_plane, position)

                # Apply rotation to align with the origin in the z axis
                rotation_matrix = do_rotation(arc_angle, rotation_axis[0])
                new_plane.rotate_plane(rotation_matrix)
                logging.info(f"Rotating {arc_angle}° around {rotation_axis[0]}-axis")


                # Check if secondary angle changed (requires additional rotation)
                if secondary_axis[idx] != current_secondary:
                    correction_angle = current_secondary - secondary_axis[idx]

                    logging.debug(f"Since plane {idx} secondary {current_secondary} != {secondary_axis[idx]}")
                    logging.info(f"Rotating {-correction_angle}° around {rotation_axis[1]}-axis")

                    # correction_angle = 45
                    new_plane.rotate_plane(do_rotation(-correction_angle, rotation_axis[1]))
                    current_secondary = secondary_axis[idx]


                # Apply translation
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
        logging.debug(f"Trace {idx}: Type = {type(trace)}, Name = {trace.name if hasattr(trace, 'name') else 'Unnamed'}")


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

    sensorPlane.title = "Parent axis"
    sensorPlane.print_pose()

    # sourcePlane.plot_axis(fig)

    sourcePlane.title = "Source plane"
    sourcePlane.print_pose()

    #        ----- Step 4: Arc movements -----        #
    # -- Phase 1: Compute arc steps -- #
    # Gets all position P vectors for the plane as it rotates around arc
    # Increments first through arc_theta_angles, then phis
    horizontal_circles = 0

    if horizontal_circles == 1:
        arc_phi_angle = np.arange(90, -config.arc_movement["arc_phi_step"], -config.arc_movement["arc_phi_step"])
        arc_theta_angle = config.arc_movement["arc_theta_angle"]
        sequence_ID = 2  # 2 for horizontal circles movement
        rotation_axis = ["z", "y"]
        rotation_step = np.radians(config.arc_movement["arc_theta_angle"])
    else:
        print("Vertical circles movement")
        arc_phi_angle = 10
        arc_theta_angle = [0, 45]
        sequence_ID = 1  # 1 for vertical circles movement
        rotation_axis = ["y", "z"]
        rotation_step = np.radians(-arc_phi_angle)


    all_positions, secondary_movement = rotation_rings(
        sequence_ID,
        config.arc_movement["radius"],  # Radius of arc movement
        arc_theta_angle,# steps of theta taken around the arc
        arc_phi_angle  # phi levels to the spherical arc
    )

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
    logging.debug(f"Figure content evaluation")
    check_fig_data(fig)
    line_scatter_objects = []
    results = np.zeros((len(rotated_planes), 2))

    for idx, plane in enumerate(rotated_planes):  # Check lines for each plane
        update_lines_global_positions(lines, plane)
        logging.debug(f"Checking intersections for plane {idx} {plane.title}")
        hit, miss = evaluate_line_results(sensorPlane, sensorAreas, aperturePlane, aperture_areas, lines)
        handle_results(sensorAreas)
        logging.info(f"Plane {plane.title} has {hit} hits and {miss} misses \n")

        results[idx, 0] = hit
        results[idx, 1] = miss

        lines_for_plane = []
        for line in lines:
            lines_for_plane.append(visualise_intersections_seq(line))  # Stores line objects for current plane
        # Stores line objects for all planes
        line_scatter_objects.append(lines_for_plane)

    #        ----- Step 7: Display the plot and results -----        #
    # Show any plot
    if config.visualization["show_output_parent"]:

        # show animation or static plot
        if config.visualization["animated_plot"]:
            fig = generate_arc_animation(fig, rotated_planes, line_scatter_objects, results)
        else:
            fig = generate_static_arc_plot(fig, rotated_planes, line_scatter_objects)
            logging.info("Static plot generated.")

        fig.show()
    else:
        logging.debug("Visualization disabled (show_output_parent = false).")

    print("\nFinished.    \n")


if __name__ == "__main__":
    main()
