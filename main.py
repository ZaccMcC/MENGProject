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
    source_plane_position = np.array([0, 0, 2])
    source_plane_direction = np.array([0, 0, 1])
    sourcePlane = Plane("Source Plane", source_plane_position, source_plane_direction, 10, 10)

    # Define the sensor plane
    sensor_plane_position = np.array([0, 0, 0]) # Defines its position (centre point)
    sensor_plane_direction = np.array([0, 0, 1]) # Defines its direction (facing down)
    sensorPlane = Plane("Sensor Plane", sensor_plane_position, sensor_plane_direction, 10, 10)

    # Define the intermediate plane
    inter_plane_position = np.array([0, 0, 1])
    inter_plane_direction = np.array([0, 0, 1])
    interPlane = Plane("Inter-plane", inter_plane_position, inter_plane_direction, 5, 5)

    # Define the sensor area (target area on the sensor plane)
    sensor_area_position = np.array([4, 3, 0])
    sensor_area_direction = np.array([0, 0, 1])
    sensorArea = Areas("Sensor", sensor_area_position, sensor_area_direction, 2, 2)

    return sensorPlane, sourcePlane, interPlane, sensorArea

def initialise_3d_plot(sourcePlane):
    """
    Initialises a 3D plot using Plotly.
    Generates a global axis for the plot.

    Returns: A Plotly figure object.
    """
    lims = 10
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

    return fig, hit, miss

def do_rotation(degrees, axis):
    theta = np.radians(degrees)
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

def main():
    """
    Runs the main program
        initialising objects, visualising,
    and
        evaluating line-plane intersections.
    """
    # Step 1: Initialize planes and areas
    sensorPlane, sourcePlane, interPlane, sensorArea = initialise_planes_and_areas()

    # Step 2: Create 3D plot and visualize environment
    fig = initialise_3d_plot(sourcePlane)
    fig = visualise_environment(fig, sensorPlane, "red")
    fig = visualise_environment(fig, sourcePlane, "yellow")
    # fig = visualise_environment(fig, interPlane, "green")
    fig = visualise_environment(fig, sensorArea, "#00FF00")

    thetaD = 45
    theta = np.radians(thetaD)
    # X-axis Rotation
    rotated_plane_x = Plane(f"Rotated {theta} degrees in x-axis",
                            sourcePlane.position,
                            sourcePlane.direction,
                            sourcePlane.width,
                            sourcePlane.length)

    rotated_plane_x.rotate_plane(do_rotation(45, "x"))
    rotated_plane_x.translate_plane(np.array([0, 5, 0]))
    fig = visualise_environment(fig, rotated_plane_x, "green")


    # Step 3: Generate random points and create lines
    direction = np.array([0, 0, 1])  # Direction vector for all lines
    lines = create_lines_from_random_points(sourcePlane, num_points=60, direction=direction)

    # Step 4: Evaluate hits and visualize lines
    fig, hit, miss = evaluate_hits_and_visualize(fig, sensorPlane, sensorArea, lines)

    # Step 5: Display the plot and results
    print(f"Total number of hits recorded: {hit}")
    print(f"Total number of misses recorded: {miss}")

    fig.show()


if __name__ == "__main__":
    main()
