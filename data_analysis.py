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

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# ---- Plot 1: Hit Percentage per Arc Position ---- #
for ray_count in df["ray count"].unique():
    subset = df[df["ray count"] == ray_count]
    grouped = subset.groupby("idx")[["hits", "misses"]].mean()
    grouped["hit_percentage"] = grouped["hits"] / (grouped["hits"] + grouped["misses"]) * 100
    axes[0].plot(grouped.index, grouped["hit_percentage"], marker="o", label=f"Ray Count: {ray_count}")

axes[0].set_title("Hit Percentage per Arc Position for Different Ray Counts")
axes[0].set_xlabel("Arc Position Index (idx)")
axes[0].set_ylabel("Hit Percentage (%)")
axes[0].grid(True)
axes[0].legend(title="Ray Count")

# --------------------------
# Load and process sensor_results.csv
# --------------------------
sensor_results_path = "sensor_results.csv"
if not os.path.exists(sensor_results_path):
    raise FileNotFoundError("Missing sensor_results.csv")

sensor_results_df = pd.read_csv(sensor_results_path)
sensor_results_df.columns = [f"col_{i}" for i in range(sensor_results_df.shape[1])]
sensor_results_df = sensor_results_df.rename(columns={"col_0": "sim", "col_1": "idx"})

# Dynamically parse sensors
records = []
num_sensors = (sensor_results_df.shape[1] - 2) // 2

for row in sensor_results_df.itertuples(index=False):
    sim = row.sim
    idx = row.idx
    for i in range(2, 2 + num_sensors * 2, 2):
        sensor_name = getattr(row, f"col_{i}")
        hits = getattr(row, f"col_{i+1}")
        if pd.notna(sensor_name) and pd.notna(hits):
            records.append({
                "sim": sim,
                "idx": idx,
                "sensor": str(sensor_name).strip(),
                "hits": int(hits)
            })

sensor_df = pd.DataFrame(records)

# Calculate percentage hit per sensor
totals = sensor_df.groupby(["sim", "idx"])["hits"].sum().reset_index(name="total_hits")
merged = pd.merge(sensor_df, totals, on=["sim", "idx"])
merged["hit_pct"] = merged["hits"] / merged["total_hits"] * 100

# ---- Plot 3: Sensor Hit Percentages ---- #
for sensor, group in merged.groupby("sensor"):
    avg_pct = group.groupby("idx")["hit_pct"].mean()
    axes[1].plot(avg_pct.index, avg_pct.values, marker="o", label=sensor)

axes[1].set_title("Average Hit Percentage per Arc Position for Each Sensor")
axes[1].set_xlabel("Arc Position Index (idx)")
axes[1].set_ylabel("Hit Percentage (%)")
axes[1].grid(True)
axes[1].legend(title="Sensor")
plt.tight_layout()
plt.show()


# ---- Plot 2: Runtime vs Ray Count ---- #
# Group by ray count
grouped = df.groupby("ray count").agg({
    "hits": "sum",
    "misses": "sum",
    "runtime": "mean"
}).reset_index()

# Calculate average hit percentage and marginal gain
grouped["hit_percentage"] = grouped["hits"] / (grouped["hits"] + grouped["misses"]) * 100
grouped["hit_gain"] = grouped["hit_percentage"].diff().fillna(0)

# Create subplot layout
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# --- Subplot 1: Runtime vs Ray Count ---
axes[0].plot(grouped["ray count"], grouped["runtime"], marker="o", color="red")
axes[0].set_title("Average Runtime vs Ray Count")
axes[0].set_xlabel("Ray Count")
axes[0].set_ylabel("Runtime (s)")
axes[0].grid(True)

# --- Subplot 2: Marginal Gain in Hit % ---
axes[1].bar(grouped["ray count"], grouped["hit_gain"], color="green")
axes[1].set_title("Marginal Gain in Hit % vs Ray Count")
axes[1].set_xlabel("Ray Count")
axes[1].set_ylabel("Gain in Hit Percentage")
axes[1].grid(True)

plt.tight_layout()
plt.show()

# ---- Plot 4: Runtime, Gain, and Cost per Gain ---- #

# Group and calculate stats
grouped = df.groupby("ray count").agg({
    "hits": "sum",
    "misses": "sum",
    "runtime": "mean"
}).reset_index()

grouped["hit_percentage"] = grouped["hits"] / (grouped["hits"] + grouped["misses"]) * 100
grouped["hit_gain"] = grouped["hit_percentage"].diff().fillna(0)
grouped["runtime_gain"] = grouped["runtime"].diff().fillna(0)
grouped["cost_per_gain"] = grouped["runtime_gain"] / grouped["hit_gain"].replace(0, float("nan"))

# Plot all three metrics side-by-side
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Plot 1: Runtime
axes[0].plot(grouped["ray count"], grouped["runtime"], marker="o", color="red")
axes[0].set_title("Average Runtime vs Ray Count")
axes[0].set_xlabel("Ray Count")
axes[0].set_ylabel("Runtime (s)")
axes[0].grid(True)

# Plot 2: Hit Gain
axes[1].bar(grouped["ray count"], grouped["hit_gain"], color="green")
axes[1].set_title("Marginal Gain in Hit %")
axes[1].set_xlabel("Ray Count")
axes[1].set_ylabel("Gain in Hit Percentage")
axes[1].grid(True)

# Plot 3: Cost per Gain
axes[2].plot(grouped["ray count"], grouped["cost_per_gain"], marker="o", color="purple")
axes[2].set_title("Cost per Hit % Gain")
axes[2].set_xlabel("Ray Count")
axes[2].set_ylabel("Seconds per % Gain")
axes[2].grid(True)

plt.tight_layout()
plt.show()


# Load the results and sensor logs
results_df = pd.read_csv("results.csv")
sensor_results_df = pd.read_csv("sensor_results.csv")

# Merge ray count info into the sensor results
ray_counts = results_df[["sim", "ray count"]].drop_duplicates()
sensor_results_df = pd.merge(sensor_results_df, ray_counts, on="sim", how="left")

# Convert to long format: one row per (sim, idx, sensor)
records = []
sensor_cols = sensor_results_df.columns[2:-1:2]  # Every second column: Sensor A, B, etc.

for _, row in sensor_results_df.iterrows():
    sim = row["sim"]
    idx = row["idx"]
    ray_count = row["ray count"]
    for sensor in sensor_cols:
        hits = row[sensor]
        if pd.notna(hits):
            records.append({
                "sim": sim,
                "idx": idx,
                "sensor": sensor,
                "hits": int(hits),
                "ray count": ray_count
            })

sensor_df = pd.DataFrame(records)

# Compute total hits per (sim, idx) so we can normalize per sensor
totals = sensor_df.groupby(["sim", "idx"])["hits"].sum().reset_index(name="total_hits")
sensor_df = pd.merge(sensor_df, totals, on=["sim", "idx"])
sensor_df["hit_pct"] = sensor_df["hits"] / sensor_df["total_hits"] * 100

# Plot each (sensor x ray count) pair
plt.figure(figsize=(14, 6))
grouped = sensor_df.groupby(["sensor", "ray count", "idx"])["hit_pct"].mean().reset_index()

for (sensor, ray_count), group in grouped.groupby(["sensor", "ray count"]):
    label = f"{sensor} - {ray_count} rays"
    plt.plot(group["idx"], group["hit_pct"], marker="o", label=label)

plt.title("Sensor Hit % per Arc Position, by Ray Count")
plt.xlabel("Arc Position Index (idx)")
plt.ylabel("Hit Percentage (%)")
plt.grid(True)
plt.legend(title="Sensor × Ray Count", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()
