from arcRotation import arc_movement_coordinates, arc_movement_vector
from intersectionCalculations import intersection_wrapper  # Import for calculating line-plane intersection
from line import Line  # Import for Line object
from plane import Plane, compute_local_axes  # Import for Plane object
from areas import Areas  # Import for target areas
import numpy as np  # For mathematical operations
import plotly.graph_objects as go  # For 3D visualization

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
    sensor_plane_position = ([0, 0, 0]) # Defines its position (centre point)
    sensor_plane_direction = ([0, 0, 1]) # Defines its direction (facing down)
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

def initialise_3d_plot(sourcePlane):
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
            zaxis=dict(title="Z-Axis", range=[-lims, lims])   # Keep Z range similar
        ),
        title="3D Planes and Lines Visualization"

    )

    global_axis = compute_local_axes(sourcePlane.direction)
    axis_colours = ['red', 'green', 'blue']
    axis_names = ['Right', 'Up', 'Normal']

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

    fig.update_traces(showlegend = True)
    return fig

def visualise_environment(fig, planeObject, colour): # sensorPlane, sourcePlane, interPlane, sensorArea):
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
    else :
        print("Invalid axis")
        R = np.array([1,1,1])
    return R

# def incremental_movements():


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

    # Step 1: Initialize planes and areas
    sensorPlane, sourcePlane, interPlane, sensorArea = initialise_planes_and_areas()

    # Step 2: Create lines from source plane
    lines = create_lines_from_random_points(sourcePlane, num_points=60, direction=sourcePlane.direction)

    # Step 3: Create 3D plot and visualize environment
    fig = initialise_3d_plot(sourcePlane)
    fig = visualise_environment(fig, sensorPlane, "red")
    fig = visualise_environment(fig, sourcePlane, "yellow")
    # fig = visualise_environment(fig, interPlane, "green")
    # fig = visualise_environment(fig, sensorArea, "#00FF00")

    # Step 4: Apply translation / rotation to original source plane
    radius = 9 # Starting position for arc movement
    theta = 90 # Degrees of rotation

    translation = np.array([radius, 0 ,-1]) # Translation vector -> arc starting position
    rotationAxis = "y" # Specify axis of rotation

    # Create copy of course plane
    #
    new_source_plane = Plane(f"Copy of source",
                            sourcePlane.position,
                            sourcePlane.direction,
                            sourcePlane.width,
                            sourcePlane.length)

    # Before movement from initial position to arc starting position
    new_source_plane.print_pose()

    # Apply rotation
    new_source_plane.rotate_plane(do_rotation(np.radians(theta), rotationAxis))
    new_source_plane.title = f"Plane rotated {theta:.0f}° in {rotationAxis}-axis"
    new_source_plane.print_pose()

    # Apply translation
    new_source_plane.translate_plane(translation)
    new_source_plane.title = f"Plane translated by [{translation[0]:.2f}, {translation[1]:.2f},{translation[2]:.2f}]"
    new_source_plane.print_pose()

    # Starting position achieved


    # Visualise the new source plane
    fig = visualise_environment(fig, new_source_plane, "blue")

    # Move to first arc position
    arc_angle = 90 # Degrees of rotation around arc

    # Get coordinates of steps in arc
    nextPositions, _ = arc_movement_coordinates(arc_angle, radius)

    # Get vector required to move plane between current position and
    newVector = arc_movement_vector(new_source_plane, nextPositions[1])
    print(f"New vector: {newVector}")
    new_source_plane.plot_axis(fig)
    sourcePlane.plot_axis(fig)

    # Apply rotation
    new_source_plane.rotate_plane(do_rotation(np.radians(arc_angle), "z"))

    # Apply translation
    new_source_plane.translate_plane(newVector)
    new_source_plane.title = f"Plane translated by [{newVector[0]:.2f}, {newVector[1]:.2f},{newVector[2]:.2f}]"
    new_source_plane.print_pose()

    # # Visualise the new source plane
    fig = visualise_environment(fig, new_source_plane, "green")
    new_source_plane.plot_axis(fig)

    # # Step 5: Rotate lines
    # for i in lines:
    #     i.update_position(new_source_plane)

    # Step 5: Evaluate hits and visualize lines
    # fig, hit, miss = evaluate_hits_and_visualize(fig, sensorPlane, sensorArea, lines)

    # Step 6: Display the plot and results
    try:
        fig.show()
        print("\n   🚨    \n")
    except Exception as e:
        print(f"Plotly Error: {e}")
        exit(1)

    # new_source_plane.print_pose()
if __name__ == "__main__":
    main()