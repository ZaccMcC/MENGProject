import pandas as pd
import matplotlib.pyplot as plt
import os

# Load results.csv (now contains runtime)
results_path = "results.csv"

if not os.path.exists(results_path):
    raise FileNotFoundError("Missing results.csv")

# Load results
df = pd.read_csv(results_path)

# ---- Plot 1: Hit Percentage per Arc Position ---- #
plt.figure(figsize=(10, 6))

for ray_count in df["ray count"].unique():
    subset = df[df["ray count"] == ray_count]
    grouped = subset.groupby("idx")[["hits", "misses"]].mean()
    grouped["hit_percentage"] = grouped["hits"] / (grouped["hits"] + grouped["misses"]) * 100

    plt.plot(grouped.index, grouped["hit_percentage"], marker="o", label=f"Ray Count: {ray_count}")

plt.title("Hit Percentage per Arc Position for Different Ray Counts")
plt.xlabel("Arc Position Index (idx)")
plt.ylabel("Hit Percentage (%)")
plt.grid(True)
plt.legend(title="Ray Count")
plt.tight_layout()
plt.show()

# ---- Plot 2: Runtime vs Ray Count ---- #
# Average runtime per simulation (not per idx), so drop duplicates
avg_runtime_per_sim = df.drop_duplicates(subset="sim").groupby("ray count")["runtime"].mean()

plt.figure(figsize=(8, 5))
plt.plot(avg_runtime_per_sim.index, avg_runtime_per_sim.values, marker="o", color="red")
plt.title("Average Runtime vs Ray Count")
plt.xlabel("Ray Count (Number of Lines)")
plt.ylabel("Average Runtime (seconds)")
plt.grid(True)
plt.tight_layout()
plt.show()
