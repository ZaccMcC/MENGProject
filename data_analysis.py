import pandas as pd
import matplotlib.pyplot as plt
import os

# --------------------------
# Load results.csv (main summary)
# --------------------------
results_path = "results.csv"
if not os.path.exists(results_path):
    raise FileNotFoundError("Missing results.csv")

df = pd.read_csv(results_path)

# ---- Plot 1: Hit Percentage per Arc Position by Ray Count ---- #
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for ray_count in df["ray count"].unique():
    subset = df[df["ray count"] == ray_count]
    grouped = subset.groupby("idx")[["hits", "misses"]].mean()
    grouped["hit_percentage"] = grouped["hits"] / (grouped["hits"] + grouped["misses"]) * 100
    axes[0].plot(grouped.index, grouped["hit_percentage"], marker="o", label=f"{ray_count} rays")

axes[0].set_title("Overall Hit % per Arc Position by Ray Count")
axes[0].set_xlabel("Arc Position Index (idx)")
axes[0].set_ylabel("Hit Percentage (%)")
axes[0].grid(True)
axes[0].legend(title="Ray Count")

# --------------------------
# Load sensor_results.csv (new layout)
# --------------------------
sensor_path = "sensor_results.csv"
if not os.path.exists(sensor_path):
    raise FileNotFoundError("Missing sensor_results.csv")

sensor_df = pd.read_csv(sensor_path)

# Melt wide sensor data into long format
sensor_long_df = sensor_df.melt(id_vars=["sim", "idx"],
                                var_name="sensor",
                                value_name="hits")

# Normalize sensor hits per arc step
totals = sensor_long_df.groupby(["sim", "idx"])["hits"].sum().reset_index(name="total_hits")
sensor_long_df = pd.merge(sensor_long_df, totals, on=["sim", "idx"])
sensor_long_df["hit_pct"] = sensor_long_df["hits"] / sensor_long_df["total_hits"] * 100

# Average sensor hit % across all simulations
grouped_sensors = sensor_long_df.groupby(["sensor", "idx"])["hit_pct"].mean().reset_index()

# ---- Plot 2: Average Sensor Hit % per Arc Position ---- #
for sensor, group in grouped_sensors.groupby("sensor"):
    axes[1].plot(group["idx"], group["hit_pct"], marker="o", label=sensor)

axes[1].set_title("Average Hit % per Arc Position by Sensor")
axes[1].set_xlabel("Arc Position Index (idx)")
axes[1].set_ylabel("Hit Percentage (%)")
axes[1].grid(True)
axes[1].legend(title="Sensor")

plt.tight_layout()
plt.show()

# ---- Plot 3: Runtime and Marginal Gain ---- #
grouped_runtime = df.groupby("ray count").agg({
    "hits": "sum",
    "misses": "sum",
    "runtime": "mean"
}).reset_index()

grouped_runtime["hit_percentage"] = grouped_runtime["hits"] / (grouped_runtime["hits"] + grouped_runtime["misses"]) * 100
grouped_runtime["hit_gain"] = grouped_runtime["hit_percentage"].diff().fillna(0)

# ---- Plot 2: Cost per Gain Analysis ---- #
grouped_runtime["runtime_gain"] = grouped_runtime["runtime"].diff().fillna(0)
grouped_runtime["cost_per_gain"] = grouped_runtime["runtime_gain"] / grouped_runtime["hit_gain"].replace(0, float("nan"))

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Plot 1: Runtime
axes[0].plot(grouped_runtime["ray count"], grouped_runtime["runtime"], marker="o", color="red")
axes[0].set_title("Average Runtime vs Ray Count")
axes[0].set_xlabel("Ray Count")
axes[0].set_ylabel("Runtime (s)")
axes[0].grid(True)

# Plot 2: Hit Gain
axes[1].bar(grouped_runtime["ray count"], grouped_runtime["hit_gain"], color="green")
axes[1].set_title("Marginal Gain in Hit %")
axes[1].set_xlabel("Ray Count")
axes[1].set_ylabel("Gain in Hit Percentage")
axes[1].grid(True)

# Plot 3: Cost per Gain
axes[2].plot(grouped_runtime["ray count"], grouped_runtime["cost_per_gain"], marker="o", color="purple")
axes[2].set_title("Cost per Hit % Gain")
axes[2].set_xlabel("Ray Count")
axes[2].set_ylabel("Seconds per % Gain")
axes[2].grid(True)

plt.tight_layout()
plt.show()