import pandas as pd
from scipy.interpolate import interp1d
import os
import numpy as np  # For mathematical operations
import matplotlib.pyplot as plt


def define_plot(sensor_results, p_data, axs, title, x_label, y_label):
    """
    Makes plots for subplot

    :param sensor_results:
    :param p_data:
    :param axs:
    :return:
    """
    for column in sensor_results.columns:
        axs.plot(p_data, sensor_results[column], label=column)

    # Step 3: Customise the plot
    axs.set_title(f'{title} Illumination per Sensor')
    axs.set_xlabel(f'{x_label}')
    axs.set_ylabel(f'{y_label}')
    axs.legend()
    axs.grid(True)


def prepare_result_data(results_data_frame, area_column_start, area_column_end=None):
    """

    :return:
    """
    # Extract sensor data
    area_data = results_data_frame.iloc[:, area_column_start: area_column_end]

    # Extract index
    position_data = results_data_frame.iloc[:, 1]

    return area_data, position_data


def results_comparison(sim_sensor_results, sim_sensor_position, angle_data, phy_sensor_results, phy_sensor_position, phy_sensor_results_n, phy_sensor_position_n):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Populate with experimental data
    define_plot(sim_sensor_results, sim_sensor_position, axes[0], "Simulated", "Position (index)", "Hits")

    # Populate with actual data
    define_plot(phy_sensor_results, phy_sensor_position, axes[1], "Experimental (Filtered)", "Time (ms)", "Voltage")

    # define_plot(sim_sensor_results, sim_sensor_position, axes[1, 0], "Simulated")

    # # Populate with experimental data
    # define_plot(phy_sensor_results_n, phy_sensor_position_n, axes[1,1], "Experimental (Noisy)")

    # Step 4: Show the plot
    plt.show()

    # --------------------------
    # Scale simulated results as a %
    # --------------------------

    sim_sensor_results, _ = prepare_result_data(simulated_data, 2)

    arc_angles = angle_data["arc_angle_deg"].unique()
    sim_sensor_position = arc_angles

    scaled_sim_sensor_results = (sim_sensor_results / total_rays) * 100

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Populate with experimental data
    define_plot(scaled_sim_sensor_results, sim_sensor_position, axes[0], "Simulated", "Arc angle (degrees)", "Hits (as a % of total rays)")

    # Populate with actual data
    define_plot(phy_sensor_results, phy_sensor_position, axes[1], "Experimental (Filtered)", "Time (ms)", "Voltage")

    plt.show()


    # --------------------------
    # Create combined data frame
    # --------------------------
    #  Make a copy of the angle data and apply the offset
    angle_data["tilt_angle_physical_ref"] = angle_data["tilt_angle_deg"] + 90

    # print(angle_data["tilt_angle_physical_ref"])

    # If needed, wrap around 360 degrees (optional, only if angles might go over 360)
    angle_data["tilt_angle_physical_ref"] = angle_data["tilt_angle_physical_ref"] % 360

    # Combine scaled sensor results with both arc and adjusted tilt angles
    combined_df = scaled_sim_sensor_results.copy()
    combined_df["tilt_angle_deg_physical"] = angle_data["tilt_angle_physical_ref"].values
    combined_df["arc_angle_deg"] = angle_data["arc_angle_deg"].values

    # Static angle tests from experimental results
    target_angles = [
        (90, 90),
        (130, 130),
        (20, 20),
        (160, 160),
        (50, 50)
    ]

    filtered_df = combined_df[
        combined_df[["tilt_angle_deg_physical", "arc_angle_deg"]]
        .apply(tuple, axis=1)
        .isin(target_angles)
    ]

    filename = "../../output/combined_simulation_data_physical_reference.csv"
    write_header = not os.path.isfile(filename)

    # Save filtered rows only
    filtered_df.to_csv(
        filename,
        mode='a',
        header=write_header,
        index=False
    )

def sensor_surface_plots(angle_df, sensor_data):

    num_sensors = sensor_data.shape[1]

    # num_sensors = 1 # placeholder for testing

    cols = int(np.ceil(np.sqrt(num_sensors)))
    rows = int(np.ceil(num_sensors / cols))

    print(f"Number of columns: {cols} | Number of rows: {rows}")

    # Create subplots with 3D axes
    fig, axes = plt.subplots(rows, cols, figsize=(18, 5),
                             subplot_kw={'projection': '3d'})


    # Flatten axes for easier indexing (needed if rows > 1 or cols > 1)
    if rows * cols > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    for idx in range(num_sensors):

        # Prepare data
        combined = angle_df.copy()
        combined["sensor_response"] = sensor_data.iloc[:, idx].values

        # Create meshgrid
        pivot = combined.pivot(index="tilt_angle_deg", columns="arc_angle_deg", values="sensor_response")
        X, Y = np.meshgrid(pivot.columns.values, pivot.index.values)
        Z = pivot.values

        print(f"X, Y, Z shapes | {X.shape}, {Y.shape}, {Z.shape}")
        print(f"Sensor {idx}: min={np.nanmin(Z):.2f}, max={np.nanmax(Z):.2f}, NaNs: {np.isnan(Z).sum()}")


        row = 0 if idx < 2 else 1
        col = 0 if idx % 2 == 0 else 1

        # Plot surface on the corresponding subplot
        axes[idx].plot_surface(X, Y, Z, cmap='plasma')
        axes[idx].set_title(f"Sensor {sensor_data.columns[idx]}")
        axes[idx].set_xlabel('θ°')
        axes[idx].set_ylabel('φ°')
        axes[idx].set_zlabel('Sensor Illumination (Hits)')


    fig.suptitle('Sensor Response Surface Plots', fontsize=16, x=0.5, fontweight='bold', ha='center', va='center')
    fig.text(0.5, 0.93, 'Theta Arc Angle (θ) | Phi Tilt Angle (φ)', ha='center', fontsize=12)

    plt.show()

# --------------------------
# Simulated data
# --------------------------

# Simulated data input
simulated_data = pd.read_csv('../../data/sensor_results.csv')

# Prepare simulated data
sim_sensor_results, sim_sensor_position = prepare_result_data(simulated_data, 2)

simulation_info = pd.read_csv('../../data/results.csv')

total_rays = simulation_info.iloc[1, 4]

angle_data = pd.read_csv("../../data/rigid_arc_angles.csv")

# --------------------------
# Physical data
# --------------------------

# Physical data input
physical_data = pd.read_csv('../../data/physical_data_messy.csv')

# Prepare physical data
phy_sensor_results, phy_sensor_position = prepare_result_data(physical_data, 6)

# Prepare physical data
phy_sensor_results_n, phy_sensor_position_n = prepare_result_data(physical_data, 2, 6)

print(sim_sensor_results.shape)
print(sim_sensor_results.sample(n=5, random_state=42))

sensor_surface_plots(angle_data, sim_sensor_results)

results_comparison(sim_sensor_results, sim_sensor_position, angle_data, phy_sensor_results, phy_sensor_position, phy_sensor_results_n, phy_sensor_position_n)