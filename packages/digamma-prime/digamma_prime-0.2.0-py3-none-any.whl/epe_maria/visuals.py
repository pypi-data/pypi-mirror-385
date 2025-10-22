import matplotlib.pyplot as plt
import numpy as np

def plot_phi_curve(shift_vals, phi_vals, title="Structural Divergence φ vs Shift"):
    plt.figure(figsize=(8,5))
    plt.plot(shift_vals, phi_vals, marker='o', color='purple', label='φ')
    plt.xlabel("Shift Magnitude (σ)")
    plt.ylabel("φ (mean abs diff)")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("docs/images/phi_curve.png")
    plt.close()

def plot_delta_phi_curve(shift_vals, delta_vals, title="Rate Divergence Δφ vs Shift"):
    plt.figure(figsize=(8,5))
    plt.plot(shift_vals, delta_vals, marker='o', color='red', label='Δφ')
    plt.xlabel("Shift Magnitude (σ)")
    plt.ylabel("Δφ (mean abs diff of diffs)")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("docs/images/delta_phi_curve.png")
    plt.close()

def plot_surface_comparison(f_vals, g_vals, domain, title="Function Comparison with φ Region"):
    plt.figure(figsize=(8,5))
    plt.plot(domain, f_vals, label='f(x)', color='blue')
    plt.plot(domain, g_vals, label='g(x)', color='orange')
    plt.fill_between(domain, f_vals, g_vals, color='purple', alpha=0.3, label='φ region')
    plt.xlabel("x")
    plt.ylabel("Prediction")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("docs/images/surface_comparison.png")
    plt.close()


def plot_symbolic_series(x, series_list, labels=None):
    import matplotlib.pyplot as plt
    for i, series in enumerate(series_list):
        label = labels[i] if labels else f"Series {i+1}"
        plt.plot(x, series, label=label)
    plt.legend()
    plt.title("Symbolic Mollification Demo")
    plt.xlabel("x")
    plt.ylabel("Value")
    plt.grid(True)
    plt.show()

def plot_divergence_map(divergence, title="Kernel-Based Structural Drift"):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8,5))
    plt.plot(divergence, color='green', label='Divergence')
    plt.xlabel("Index")
    plt.ylabel("Divergence Magnitude")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
