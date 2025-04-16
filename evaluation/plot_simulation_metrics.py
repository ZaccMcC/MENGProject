# evaluation/plot_simulation_metrics.py

import os

import matplotlib.pyplot as plt
import pandas as pd
from evaluation.utils_io import load_csv

from evaluation.utils_metrics import compute_hit_percentage, compute_cost_per_gain

def plot_overall_hit_percentage():
    df = load_csv("C:/Users/temp/IdeaProjects/MENGProject/data/results.csv")

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    for ray_count in df["ray count"].unique():
        subset = df[df["ray count"] == ray_count]
        grouped = subset.groupby("idx")[["hits", "misses"]].mean()
        grouped["hit_percentage"] = compute_hit_percentage(grouped)
        axs[0].plot(grouped.index, grouped["hit_percentage"], marker="o", label=f"{ray_count} rays")

    axs[0].set_title("Hit % per Arc Index by Ray Count")
    axs[0].set_xlabel("Arc Index (idx)")
    axs[0].set_ylabel("Hit Percentage (%)")
    axs[0].legend()
    axs[0].grid(True)
    # plt.tight_layout()
    # plt.show()

    fig.suptitle("Sensor Performance Analysis", fontsize=16)

    return axs


def plot_sensor_hit_distribution(axs):
    df = load_csv("C:/Users/temp/IdeaProjects/MENGProject/data/sensor_results.csv")

    melted = df.melt(id_vars=["sim", "idx"], var_name="sensor", value_name="hits")
    totals = melted.groupby(["sim", "idx"])["hits"].sum().reset_index(name="total_hits")
    merged = pd.merge(melted, totals, on=["sim", "idx"])
    merged["hit_pct"] = merged["hits"] / merged["total_hits"] * 100

    avg_sensor_hits = merged.groupby(["sensor", "idx"])["hit_pct"].mean().reset_index()

    # fig, ax = plt.subplots(figsize=(10, 5))
    for sensor, group in avg_sensor_hits.groupby("sensor"):
        axs[1].plot(group["idx"], group["hit_pct"], marker="o", label=sensor)

    axs[1].set_title("Average Sensor Hit % per Arc Position")
    axs[1].set_xlabel("Arc Index (idx)")
    axs[1].set_ylabel("Hit Percentage (%)")
    axs[1].legend()
    axs[1].grid(True)
    plt.tight_layout()
    plt.show()



def plot_runtime_vs_gain():
    df = load_csv("C:/Users/temp/IdeaProjects/MENGProject/data/results.csv")
    grouped = df.groupby("ray count").agg({
        "hits": "sum",
        "misses": "sum",
        "runtime": "mean"
    }).reset_index()

    grouped["hit_percentage"] = compute_hit_percentage(grouped)
    grouped["hit_gain"] = grouped["hit_percentage"].diff().fillna(0)
    grouped["cost_per_gain"] = compute_cost_per_gain(grouped["runtime"], grouped["hit_percentage"])

    fig, axs = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Model Evaluation", fontsize=16)

    axs[0].plot(grouped["ray count"], grouped["runtime"], marker="o", color="red")
    axs[0].set_title("Average Runtime vs Ray Count")
    axs[0].set_xlabel("Ray Count")
    axs[0].set_ylabel("Runtime (s)")
    axs[0].grid(True)

    axs[1].bar(grouped["ray count"], grouped["hit_gain"], color="green")
    axs[1].set_title("Marginal Gain in Hit %")
    axs[1].set_xlabel("Ray Count")
    axs[1].set_ylabel("Hit % Gain")
    axs[1].grid(True)

    axs[2].plot(grouped["ray count"], grouped["cost_per_gain"], marker="o", color="purple")
    axs[2].set_title("Cost per Hit % Gain")
    axs[2].set_xlabel("Ray Count")
    axs[2].set_ylabel("Seconds per % Gain")
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()

def prepare_result_data(df, start_col, end_col=None):
    data = df.iloc[:, start_col:end_col] if end_col else df.iloc[:, start_col:]
    position = df.iloc[:, 1]  # 'idx' or time
    return data, position

def define_plot(ax, sensor_df, x_data, title, x_label, y_label):
    for column in sensor_df.columns:
        ax.plot(x_data, sensor_df[column], label=column)
    ax.set_title(f'{title} Illumination per Sensor')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()
    ax.grid(True)

def compare_sim_vs_real():
    sim_df = load_csv('C:/Users/temp/IdeaProjects/MENGProject/data/sensor_results.csv')
    sim_sensor, sim_pos = prepare_result_data(sim_df, 2)

    phy_df = load_csv('C:/Users/temp/IdeaProjects/MENGProject/data/physical_data_messy.csv')
    phy_sensor_filtered, phy_pos_filtered = prepare_result_data(phy_df, 6)
    phy_sensor_noisy, phy_pos_noisy = prepare_result_data(phy_df, 2, 6)

    angle_df = load_csv('C:/Users/temp/IdeaProjects/MENGProject/data/rigid_arc_angles.csv')
    sim_sensor_percent = (sim_sensor / sim_sensor.sum(axis=1).values[:, None]) * 100
    arc_angles = angle_df['arc_angle_deg'].unique()


    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    fig.suptitle("Sensor Performance Analysis", fontsize=16)

    define_plot(axes[0], sim_sensor, sim_pos, "Simulated", "Arc Position", "Hits")
    define_plot(axes[1], phy_sensor_filtered, phy_pos_filtered, "Experimental (Filtered)", "Time (ms)", "Voltage")
    plt.tight_layout()
    plt.show()

    # --- Scaled version with percentage ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    fig.suptitle("Sensor Performance Analysis", fontsize=16)

    define_plot(axes[0], sim_sensor_percent, arc_angles, "Simulated (Scaled)", "Arc Angle (deg)", "% of Rays")
    define_plot(axes[1], phy_sensor_filtered, phy_pos_filtered, "Experimental (Filtered)", "Time (ms)", "Voltage")
    plt.tight_layout()
    plt.show()

    # --- Output combined dataframe for selected angles ---
    angle_df['tilt_angle_physical_ref'] = (angle_df['tilt_angle_deg'] + 90) % 360
    combined_df = sim_sensor_percent.copy()
    combined_df['tilt_angle_deg_physical'] = angle_df['tilt_angle_physical_ref'].values
    combined_df['arc_angle_deg'] = angle_df['arc_angle_deg'].values

    target_angles = [(90, 90), (130, 130), (20, 20), (160, 160), (50, 50)]
    filtered = combined_df[
        combined_df[["tilt_angle_deg_physical", "arc_angle_deg"]].apply(tuple, axis=1).isin(target_angles)
    ]

    output_path = "C:/Users/temp/IdeaProjects/MENGProject/output/combined_simulation_data_physical_reference.csv"
    write_header = not os.path.exists(output_path)
    filtered.to_csv(output_path, mode='a', header=write_header, index=False)
    print(f"Filtered simulation data saved to {output_path}")


def run_all():
    axs_plot = plot_overall_hit_percentage()
    plot_sensor_hit_distribution(axs_plot)
    plot_runtime_vs_gain()

    compare_sim_vs_real()

if __name__ == "__main__":
    run_all()
