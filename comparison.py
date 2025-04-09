import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import numpy as np
import json


def set_axes_equal(ax):
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


def draw_rectangle(ax, centre, width, length, z, label, colour='green', alpha=0.5):
    x, y = centre
    corners = np.array([
        [x - width / 2, y - length / 2, z],
        [x + width / 2, y - length / 2, z],
        [x + width / 2, y + length / 2, z],
        [x - width / 2, y + length / 2, z]
    ])
    rect = Poly3DCollection([corners], facecolors=colour, alpha=alpha, edgecolors='k')
    ax.add_collection3d(rect)
    # Add label and coordinates
    label_text = f"{label}\n({x:.2f}, {y:.2f})"
    ax.text(x, y, z + 0.1, label_text, ha='center', va='bottom', fontsize=8)

def draw_aperture_between(ax, sensor1, sensor2, sensor_dim, z=1.0, label="Aperture", colour='gray'):
    s1 = np.array(sensor1)
    s2 = np.array(sensor2)
    centre = (s1 - s2) / 2

    vec = s2 - s1
    aligned_axis = np.argmax(np.abs(vec[:2]))  # 0 = X, 1 = Y
    # Width = along the aligned axis
    # Length = perpendicular to the aligned axis
    width = 3 * sensor_dim if aligned_axis == 0 else sensor_dim
    length = 3 * sensor_dim if aligned_axis == 1 else sensor_dim

    draw_rectangle(ax, centre[:2], width, length, z, label, colour=colour, alpha=0.3)


def do_plotting(ax, sensor_pair_gap):
    ax.clear()

    origin = [0, 0, 0]
    sensor_dim = 1.5
    initial_gap_origin = 0.5

    # Vertical pair (Sensors 0 and 1)
    sensor_1_centre = [origin[0], origin[1] - initial_gap_origin - sensor_dim / 2, 0]
    sensor_0_centre = [origin[0], sensor_1_centre[1] - sensor_dim - sensor_pair_gap, 0]

    # Horizontal pair (Sensors 2 and 3)
    sensor_2_centre = [origin[0] + initial_gap_origin + sensor_dim / 2, origin[1] + initial_gap_origin + sensor_dim / 2, 0]
    sensor_3_centre = [origin[0] - initial_gap_origin - sensor_dim / 2, origin[1] + initial_gap_origin + sensor_dim / 2, 0]

    centers = [sensor_0_centre, sensor_1_centre, sensor_2_centre, sensor_3_centre]
    labels = ["Sensor 0", "Sensor 1", "Sensor 2", "Sensor 3"]

    aperture_1 = (np.array(sensor_0_centre) + np.array(sensor_1_centre))/2


    for idx, center in enumerate(centers):
        draw_rectangle(ax, center[:2], sensor_dim, sensor_dim, center[2], labels[idx])
        draw_aperture_between(ax, sensor_0_centre, sensor_1_centre, sensor_dim, z=1.0, label="Aperture A")
        draw_aperture_between(ax, sensor_2_centre, sensor_3_centre, sensor_dim, z=1.0, label="Aperture B")

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'3D Sensor Layout - Pair Gap: {sensor_pair_gap:.2f}')
    ax.view_init(elev=20, azim=60)
    ax.grid(True)
    set_axes_equal(ax)


def launch_gui(config):
    root = tk.Tk()
    root.title("3D Sensor Visualiser")

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_plot(val):
        gap = float(val)
        do_plotting(ax, sensor_pair_gap=gap)
        canvas.draw()

    # Initial plot
    do_plotting(ax, sensor_pair_gap=0.5)
    canvas.draw()

    # Slider widget
    slider = tk.Scale(root, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL,
                      label="Sensor Pair Gap", command=update_plot, length=400)
    slider.set(0.5)
    slider.pack(pady=10)

    root.mainloop()


# Load your config.json
with open("config.json") as f:
    config = json.load(f)

# Launch GUI with interactive slider
launch_gui(config)
