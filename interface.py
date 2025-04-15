import tkinter as tk
from tkinter import messagebox
from tkinter import font
from tkinter import ttk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import json
import ast
from config import Config
from main import run_all_test

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

CONFIG_FILE = "config.json"

READABLE_NAMES = {
    # Sections
    "planes": "Planes",
    "sensor_areas": "Sensor Areas",
    "aperture_areas": "Aperture Areas",
    "arc_movement": "Arc Movement",
    "simulation": "Simulation Settings",
    "intersection": "Intersection Controls",
    "visualization": "Visualisation",
    "debugging": "Debugging Options",
    "performance": "Performance Tuning",

    # Parameters (examples — add more as needed)
    "num_lines": "Number of Lines",
    "num_runs": "Number of Runs",
    "max_distance": "Maximum Distance",
    "strict_mode": "Strict Mode",
    "tolerance": "Tolerance",
    "show_sensor_plane": "Show Sensor Plane",
    "show_source_plane": "Show Source Plane",
    "rotation_axis": "Rotation Axis",
    "frame_rate": "Frame Rate"
}

import matplotlib.patches as patches

def plot_sensor_layout_in_frame(frame, config_obj):
    # Clear frame if there's an existing plot
    for widget in frame.winfo_children():
        widget.destroy()

    # Sim dimensions
    sim_width = 10
    sim_height = 10
    sensor_positions = get_simulated_sensor_positions()

    sensor_keys = ["sensor_A", "sensor_B", "sensor_C", "sensor_D"]

    for key, pos in zip(sensor_keys, sensor_positions):
        # Update the position field (Z = 0)
        config_obj.sensor_areas[key]["position"] = [pos[0], pos[1], 0]

    # Create a matplotlib Figure
    fig = Figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')

    # Draw the mount
    ax.add_patch(patches.Rectangle(
        (-sim_width / 2, -sim_height / 2),
        sim_width, sim_height,
        linewidth=1,
        edgecolor='black',
        facecolor='lightgrey',
        linestyle='--',
        label='Mounting Surface'
    ))

    # Plot sensors
    for idx, (x, y) in enumerate(sensor_positions):
        ax.plot(x, y, 'ro')
        ax.text(x + 0.2, y + 0.2, f"A{idx}", fontsize=9)

    ax.set_xlim(-sim_width / 2 - 1, sim_width / 2 + 1)
    ax.set_ylim(-sim_height / 2 - 1, sim_height / 2 + 1)
    ax.set_xlabel('X Position (sim units)')
    ax.set_ylabel('Y Position (sim units)')
    ax.set_title('Sensor Layout')
    ax.grid(True)
    ax.legend()

    # Embed into Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def get_simulated_sensor_positions():

    schematic_width_mm = 57
    schematic_height_mm = 62

    sim_width = 10
    sim_height = 10

    # Scale factors
    scale_x = sim_width / schematic_width_mm
    scale_y = sim_height / schematic_height_mm

    # offset to shift to origin
    center_x_mm = schematic_width_mm / 2
    center_y_mm = schematic_height_mm / 2

    # Sensor positions from schematic (in mm)
    sensor_mm_positions = [
        (28.5, 32),   # Sensor 0
        (36.5, 32),   # Sensor 1
        (44, 38),     # Sensor 2
        (44, 46)      # Sensor 3
    ]

    # Convert to simulation coordinates
    sensor_sim_positions = []
    for (x_mm, y_mm) in sensor_mm_positions:
        x_sim = (x_mm - center_x_mm) * scale_x
        y_sim = (y_mm - center_y_mm) * scale_y
        print(f"[{x_sim}, {y_sim}]")
        sensor_sim_positions.append((x_sim, y_sim))

    return sensor_sim_positions

def get_readable_name(key):
    return READABLE_NAMES.get(key, key.replace("_", " ").title())

def load_config_defaults():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)



def config_gui():
    original_config = load_config_defaults()
    entry_widgets = {}
    config_obj = Config(data=original_config)

    MIN_ITEMS_TO_GROUP = 4
    grouped_sections = []  # sections to be combined
    individual_sections = []  # sections to layout normally

    for section_name, section_data in original_config.items():
        if isinstance(section_data, dict):
            if len(section_data) <= MIN_ITEMS_TO_GROUP:
                grouped_sections.append(section_name)
            else:
                individual_sections.append(section_name)

    def combine_sections(container, section_names, start_row, start_col, num_columns):
        """
        Groups multiple small sections and packs them vertically into grid cells.
        """
        row = start_row
        col = start_col
        max_sections_per_column = 5
        grouped = 0

        for i in range(0, len(section_names), max_sections_per_column):
            frame_group = section_names[i:i + max_sections_per_column]
            combined_frame = ttk.Frame(container)
            combined_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nw")

            for section_name in frame_group:
                section_data = original_config[section_name]

                bold_font = ("Segoe UI", 11, "bold")

                sec_frame = ttk.LabelFrame(
                    combined_frame,
                    text=get_readable_name(section_name),
                    bootstyle="secondary",
                    borderwidth=5,  # Try 2–4 for more emphasis
                    relief="ridge"  # or "groove", "solid"
                )

                sec_frame.configure(labelwidget=ttk.Label(sec_frame, text=get_readable_name(section_name), font=bold_font))

                sec_frame.pack(fill="x", expand=True, pady=(0, 10))
                create_entries(sec_frame, section_name, section_data, 3)

            col += 1
            if col >= num_columns:
                col = 0
                row += 1

        return row, col  # return updated position


    def create_entries(section_frame, section_name, section_data, INTERNAL_NUM_COLUMNS):
        row_index = 0
        for key, value in section_data.items():
            col = row_index % INTERNAL_NUM_COLUMNS
            row = row_index // INTERNAL_NUM_COLUMNS

            container = ttk.Frame(section_frame)
            container.grid(row=row, column=col, sticky="ew", padx=10, pady=10)

            # ttk.Label(container, text=key, anchor="w").pack(side="top", anchor="w")
            ttk.Label(container, text=get_readable_name(key), anchor="w").pack(side="top", anchor="w")


            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                cb = ttk.Checkbutton(container, variable=var)
                cb.pack(side="top", anchor="w")
                entry_widgets[(section_name, key)] = var
            else:
                entry = ttk.Entry(container)
                entry.insert(0, str(value))
                entry.pack(side="top", fill="x", expand=True)
                entry_widgets[(section_name, key)] = entry

            row_index += 1

    def apply_and_close():
        new_config = {}
        for (section, key), widget in entry_widgets.items():
            if section not in new_config:
                new_config[section] = {}

            if isinstance(widget, tk.BooleanVar):
                new_config[section][key] = widget.get()
            else:
                text = widget.get()
                try:
                    parsed_value = ast.literal_eval(text)
                    new_config[section][key] = parsed_value
                except (ValueError, SyntaxError):
                    new_config[section][key] = text

        temp_config = Config(data=new_config)

        messagebox.showinfo("Applied", "Configuration loaded into memory.")
        root.destroy()
        run_with_config(temp_config)

    root = ttk.Window(themename="darkly")
    root.title("Edit Config for This Run")
    root.geometry("1100x900")

    style = ttk.Style()
    # style.theme_use("clam")

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=11)

    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame, bd=0, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    row = 0
    col = 0
    num_columns = 3

    visualise_frame = ttk.LabelFrame(scroll_frame, text="Sensor Layout Visualisation")
    visualise_frame.grid(row=0, column=0, columnspan=1, padx=15, pady=15, sticky="nsew")

    col += 1
    if col >= num_columns:
        col = 0
        row += 1

    # Handle grouped small sections
    row, col = combine_sections(scroll_frame, grouped_sections, row, col, num_columns)

    # Handle larger sections
    for section_name in individual_sections:
        bold_font = ("Segoe UI", 11, "bold")
        sec_frame = ttk.LabelFrame(scroll_frame, text=get_readable_name(section_name), bootstyle="secondary")
        sec_frame.configure(labelwidget=ttk.Label(sec_frame, text=get_readable_name(section_name), font=bold_font))

        sec_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nw")
        create_entries(sec_frame, section_name, original_config[section_name], 4)

        col += 1
        if col >= num_columns:
            col = 0
            row += 1

    plot_area = ttk.Frame(visualise_frame)
    plot_area.pack(fill="both", expand=True)

    # Plot from current config initially
    def plot_existing_config_layout():
        # Read sensor positions from current config
        sensor_keys = ["sensor_A", "sensor_B", "sensor_C", "sensor_D"]
        positions = [config_obj.sensor_areas[k]["position"] for k in sensor_keys]

        # Flatten to 2D for plotting
        sensor_positions = [(x, y) for x, y, _ in positions]
        update_plot(plot_area, sensor_positions)

    # Plot from schematic layout
    def plot_simulated_layout_and_update_config():
        sensor_positions = get_simulated_sensor_positions()
        sensor_keys = ["sensor_A", "sensor_B", "sensor_C", "sensor_D"]
        for key, pos in zip(sensor_keys, sensor_positions):
            config_obj.sensor_areas[key]["position"] = [pos[0], pos[1], 0]
        update_plot(plot_area, sensor_positions)


    def update_plot(frame, sensor_positions):
        for widget in frame.winfo_children():
            widget.destroy()

        sim_width = 10
        sim_height = 10

        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        ax.add_patch(patches.Rectangle(
            (-sim_width / 2, -sim_height / 2),
            sim_width, sim_height,
            linewidth=1,
            edgecolor='black',
            facecolor='lightgrey',
            linestyle='--',
            label='Mounting Surface'
        ))

        for idx, (x, y) in enumerate(sensor_positions):
            ax.plot(x, y, 'ro')
            ax.text(x + 0.2, y + 0.2, f"A{idx}", fontsize=9)

        ax.set_xlim(-sim_width / 2 - 1, sim_width / 2 + 1)
        ax.set_ylim(-sim_height / 2 - 1, sim_height / 2 + 1)
        ax.set_xlabel('X Position (sim units)')
        ax.set_ylabel('Y Position (sim units)')
        ax.set_title('Sensor Layout')
        ax.grid(True)
        ax.legend()

        fig.patch.set_facecolor("#212529")  # or match ttkbootstrap dark bg
        ax.set_facecolor("#2a2a2a")         # slightly lighter for contrast

        ax.title.set_color("white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.legend().get_frame().set_facecolor("#343a40")
        ax.legend().get_frame().set_edgecolor("white")

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Initial plot
    plot_existing_config_layout()

    # Add buttons
    btn_frame = ttk.Frame(visualise_frame)
    btn_frame.pack(pady=5)

    ttk.Button(btn_frame, text="📂 Load Existing Layout", command=plot_existing_config_layout, bootstyle="light").pack(side="left", padx=5)
    ttk.Button(btn_frame, text="🧮 Calculate Layout", command=plot_simulated_layout_and_update_config, bootstyle="light").pack(side="left", padx=5)


    for key in config_obj.sensor_areas:
        print(f"{key}: {config_obj.sensor_areas[key]['position']}")

    apply_button = ttk.Button(scroll_frame, text="✅ Apply and Run", command=apply_and_close, bootstyle="light")
    apply_button.grid(row=row, column=col, columnspan=1, pady=20)

    root.mainloop()

def run_with_config(temp_config):
    print("Custom config object created in memory")
    print(f"Planes available: {list(temp_config.planes.keys())}")
    print("Launching simulation with updated config...")
    run_all_test(temp_config, temp_config.simulation["num_lines"])

if __name__ == "__main__":
    config_gui()
