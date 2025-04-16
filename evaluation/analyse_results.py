import os
import pandas as pd
import matplotlib.pyplot as plt
from utils_io import load_csv
from utils_metrics import compute_hit_percentage, compute_cost_per_gain
import numpy as np


def get_sim_title():
    try:
        df = load_csv("../data/results.csv")
        return df["sim title"].iloc[-1]
    except:
        return "Simulation"


def plot_hit_percentage_combined():
    df = load_csv("../data/results.csv")
    sensor_df = load_csv("../data/sensor_results.csv")
    sim_title = get_sim_title()

    fig, axs = plt.subplots(1, 2, figsize=(14, 5))

    # Overall Hit % per Arc Position
    for ray_count in df["ray count"].unique():
        subset = df[df["ray count"] == ray_count]
        grouped = subset.groupby("idx")[["hits", "misses"]].mean()
        grouped["hit_percentage"] = compute_hit_percentage(grouped)
        axs[0].plot(grouped.index, grouped["hit_percentage"], marker="o", label=f"{ray_count} rays")

    axs[0].set_title("Overall Hit %")
    axs[0].set_xlabel("Arc Index (idx)")
    axs[0].set_ylabel("Hit Percentage (%)")
    axs[0].legend()
    axs[0].grid(True)

    # Per-Sensor Hit %
    melted = sensor_df.melt(id_vars=["sim", "idx"], var_name="sensor", value_name="hits")
    totals = melted.groupby(["sim", "idx"])["hits"].sum().reset_index(name="total_hits")
    merged = pd.merge(melted, totals, on=["sim", "idx"])
    merged["hit_pct"] = merged["hits"] / merged["total_hits"] * 100

    avg_sensor_hits = merged.groupby(["sensor", "idx"])["hit_pct"].mean().reset_index()

    for sensor, group in avg_sensor_hits.groupby("sensor"):
        axs[1].plot(group["idx"], group["hit_pct"], marker="o", label=sensor)

    axs[1].set_title("Per-Sensor Hit %")
    axs[1].set_xlabel("Arc Index (idx)")
    axs[1].set_ylabel("Hit Percentage (%)")
    axs[1].legend()
    axs[1].grid(True)

    plt.suptitle(f"Hit Percentage Analysis - {sim_title}", fontsize=16)
    plt.tight_layout()
    plt.show()


def plot_runtime_vs_gain():
    df = load_csv("../data/results.csv")
    grouped = df.groupby("ray count").agg({
        "hits": "sum",
        "misses": "sum",
        "runtime": "mean"
    }).reset_index()

    grouped["hit_percentage"] = compute_hit_percentage(grouped)
    grouped["hit_gain"] = grouped["hit_percentage"].diff().fillna(0)
    grouped["cost_per_gain"] = compute_cost_per_gain(grouped["runtime"], grouped["hit_percentage"])

    fig, axs = plt.subplots(1, 3, figsize=(16, 5))
    axs[0].plot(grouped["ray count"], grouped["runtime"], marker="o", color="red")
    axs[0].set_title("Average Runtime vs Ray Count")

    axs[1].bar(grouped["ray count"], grouped["hit_gain"], color="green")
    axs[1].set_title("Marginal Gain in Hit %")

    axs[2].plot(grouped["ray count"], grouped["cost_per_gain"], marker="o", color="purple")
    axs[2].set_title("Cost per Hit % Gain")

    for ax in axs:
        ax.set_xlabel("Ray Count")
        ax.grid(True)

    axs[0].set_ylabel("Runtime (s)")
    axs[1].set_ylabel("Hit % Gain")
    axs[2].set_ylabel("Seconds per % Gain")
    plt.suptitle(f"Runtime and Efficiency Analysis", fontsize=16)
    plt.tight_layout()
    plt.show()


def compare_sim_vs_real():
    sim_df = load_csv("../data/sensor_results.csv")
    phy_df = load_csv("../data/physical_data_messy.csv")
    angle_df = load_csv("../data/rigid_arc_angles.csv")

    sim_data = sim_df.iloc[:, 2:] / sim_df.iloc[:, 2:].sum(axis=1).values[:, None] * 100
    sim_pos = angle_df['arc_angle_deg'].unique()

    phy_filtered = phy_df.iloc[:, 6:]
    phy_time = phy_df.iloc[:, 1]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for col in sim_data.columns:
        axes[0].plot(sim_pos, sim_data[col], label=col)
    axes[0].set_title("Simulated (Scaled)")

    for col in phy_filtered.columns:
        axes[1].plot(phy_time, phy_filtered[col], label=col)
    axes[1].set_title("Experimental (Filtered)")

    for ax in axes:
        ax.set_xlabel("Position")
        ax.set_ylabel("Response")
        ax.grid(True)
        ax.legend()

    plt.suptitle("Simulated vs Experimental Sensor Response", fontsize=16)
    plt.tight_layout()
    plt.show()


def sensor_surface_plots():
    from mpl_toolkits.mplot3d import Axes3D

    angle_df = load_csv("../data/rigid_arc_angles.csv")
    sensor_df = load_csv("../data/sensor_results.csv")

    num_sensors = sensor_df.shape[1] - 2  # exclude sim and idx
    cols = int(np.ceil(np.sqrt(num_sensors)))
    rows = int(np.ceil(num_sensors / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(18, 6), subplot_kw={'projection': '3d'})
    if rows * cols > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    sensor_data = sensor_df.iloc[:, 2:]

    for idx in range(num_sensors):
        combined = angle_df.copy()
        combined["sensor_response"] = sensor_data.iloc[:, idx].values

        pivot = combined.pivot(index="tilt_angle_deg", columns="arc_angle_deg", values="sensor_response")
        X, Y = np.meshgrid(pivot.columns.values, pivot.index.values)
        Z = pivot.values

        axes[idx].plot_surface(X, Y, Z, cmap='plasma')
        axes[idx].set_title(f"Sensor {sensor_data.columns[idx]}")
        axes[idx].set_xlabel('Arc Angle (°)')
        axes[idx].set_ylabel('Tilt Angle (°)')
        axes[idx].set_zlabel('Hits')

    plt.suptitle(f'Sensor Response Surface Plots - {get_sim_title()}', fontsize=16)
    plt.tight_layout()
    plt.show()

def plot_per_test_summary():
    df = load_csv("../data/results.csv")
    sensor_df = load_csv("../data/sensor_results.csv")

    if "sim title" not in df.columns:
        print("Missing 'sim title' column in results.csv")
        return

    # Merge overall and sensor-level data
    sensor_df = sensor_df.copy()
    sensor_df["sim title"] = df["sim title"]  # add test names to sensor file

    grouped = df.groupby("sim title")[["hits", "misses"]].sum()
    grouped["hit_percentage"] = compute_hit_percentage(grouped)

    # Overall Hit % per Test
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))

    axs[0].bar(grouped.index, grouped["hit_percentage"], color="skyblue")
    axs[0].set_title("Overall Hit % by Test Case")
    axs[0].set_ylabel("Hit Percentage (%)")
    axs[0].tick_params(axis='x', rotation=45)
    axs[0].grid(True)

    # Per-Sensor Hit % per Test
    melted = sensor_df.melt(id_vars=["sim", "idx", "sim title"], var_name="sensor", value_name="hits")
    totals = melted.groupby(["sim title", "sim", "idx"])["hits"].sum().reset_index(name="total_hits")
    merged = pd.merge(melted, totals, on=["sim title", "sim", "idx"])
    merged["hit_pct"] = merged["hits"] / merged["total_hits"] * 100

    sensor_avg = merged.groupby(["sim title", "sensor"])["hit_pct"].mean().unstack()

    sensor_avg.plot(kind="bar", stacked=False, ax=axs[1])
    axs[1].set_title("Average Hit % per Sensor by Test")
    axs[1].set_ylabel("Hit Percentage (%)")
    axs[1].tick_params(axis='x', rotation=45)
    axs[1].legend(title="Sensor")
    axs[1].grid(True)

    plt.suptitle("Test-by-Test Summary Analysis", fontsize=16)
    plt.tight_layout()
    plt.show()


def menu():
    options = {
        "1": ("Plot Overall and Per-Sensor Hit %", plot_hit_percentage_combined),
        "2": ("Plot Runtime vs Gain and Cost Analysis", plot_runtime_vs_gain),
        "3": ("Compare Simulated vs Real Sensor Data", compare_sim_vs_real),
        "4": ("Generate Sensor Response Surface Plots", sensor_surface_plots),
        "5": ("Plot Overall and Per-Sensor Hit % by Test Case", plot_per_test_summary),
        "6": ("Exit", exit)
    }

    while True:
        print("\nSelect an analysis option:")
        for key, (desc, _) in options.items():
            print(f" {key}. {desc}")

        choice = input("Enter choice: ")
        if choice in options:
            print(f"\nRunning: {options[choice][0]}\n")
            options[choice][1]()
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    menu()
