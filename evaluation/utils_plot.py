import matplotlib.pyplot as plt

def plot_hit_rate(ax, x, y, label, marker="o"):
    ax.plot(x, y, marker=marker, label=label)
    ax.set_title("Hit Rate")
    ax.set_xlabel("Position")
    ax.set_ylabel("Hit Percentage")
    ax.legend()
    ax.grid(True)