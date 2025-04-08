import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def define_plot(sensor_results, p_data, axs):
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
    axs.set_title('Hits Over Time by Area')
    axs.set_xlabel('Time (index)')
    axs.set_ylabel('Hits')
    axs.legend()
    axs.grid(True)

def prepare_result_data(results_data_frame):
    """

    :return:
    """
    # Extract sensor data
    area_data = results_data_frame.iloc[:, 2:]

    # Extract index
    position_data = results_data_frame.iloc[:, 1]

    return area_data, position_data

# --------------------------
# Simulated data
# --------------------------

# Simulated data input
simulated_data = pd.read_csv('sensor_results.csv')

# Prepare simulated data
sim_sensor_results, sim_sensor_position = prepare_result_data(simulated_data)

# --------------------------
# Physical data
# --------------------------

# Physical data input
physical_data = pd.read_csv('physical_data.csv')

# Prepare physical data
phy_sensor_results, phy_sensor_position = prepare_result_data(physical_data)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Populate with experimental data
define_plot(sim_sensor_results, sim_sensor_position, axes[0])

# Populate with actual data
define_plot(phy_sensor_results, phy_sensor_position, axes[1])

# Step 4: Show the plot
plt.show()

# --------------------------
# Direct comparison
# --------------------------

t_sim = sim_sensor_position.to_numpy()
t_exp = phy_sensor_position.to_numpy()

# Mapping from simulation column names to experimental column names
column_map = {
    'Sensor A': 'A2(V)',
    'Sensor B': 'A3(V)',
    'Sensor C': 'A1(V)',
    'Sensor D': 'A0(V)'
}
fig, axes = plt.subplots(2, 2, figsize=(16, 6))

axes = axes.flatten()

i = 0
# Interpolation + plotting loop
for sim_col, exp_col in column_map.items():
    if sim_col in sim_sensor_results.columns and exp_col in phy_sensor_results.columns:
        # Interpolate this simulation column
        y_sim = sim_sensor_results[sim_col].to_numpy()
        interpolator = interp1d(t_sim, y_sim, kind='linear', fill_value='extrapolate')
        y_sim_interp = interpolator(t_exp)

        # Plot comparison
        # plt.figure(figsize=(10, 5))
        axes[i].plot(t_exp, phy_sensor_results[exp_col], label=f'Experimental ({exp_col})', alpha=0.6)
        axes[i].plot(t_exp, y_sim_interp, label=f'Simulation ({sim_col})', linestyle='--')
        axes[i].set_title(f'Comparison of Signals: {sim_col} ↔ {exp_col}')
        axes[i].set_xlabel('Time')
        axes[i].set_ylabel('Signal')
        axes[i].legend()
        axes[i].grid(True)

        i = i + 1

    else:
        print(f"Skipping: {sim_col} or {exp_col} not found in respective DataFrames.")

plt.show()