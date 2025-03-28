import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the results CSV
results_path = "results.csv"
if os.path.exists(results_path):
    df = pd.read_csv(results_path)
else:
    raise FileNotFoundError("The results.csv file does not exist in the expected location.")

# Initialize the plot
plt.figure(figsize=(10, 6))

# Loop through each unique ray count
for ray_count in df["ray count"].unique():
    subset = df[df["ray count"] == ray_count]

    # Group by idx and calculate mean hits/misses
    grouped = subset.groupby("idx")[["hits", "misses"]].mean()
    grouped["hit_percentage"] = grouped["hits"] / (grouped["hits"] + grouped["misses"]) * 100

    # Plot this line
    plt.plot(
        grouped.index,
        grouped["hit_percentage"],
        marker="o",
        label=f"Ray Count: {ray_count}"
    )

# Final plot settings
plt.title("Hit Percentage per Arc Position for Different Ray Counts")
plt.xlabel("Arc Position Index (idx)")
plt.ylabel("Hit Percentage (%)")
plt.grid(True)
plt.legend(title="Ray Count")
plt.tight_layout()
plt.show()