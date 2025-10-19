#!/usr/bin/env python3
"""
Plot Kendall’s τ versus Chatterjee’s ξ
with the attainable region correctly shaded
and the extrema C_{±b_0} marked.
"""

import pathlib

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


# ----------------------------------------------------------------------
#  Closed-form measures (Prop. 1)
# ----------------------------------------------------------------------
def xi_from_b(b: float) -> float:
    """Chatterjee’s ξ(C_b) – even in b."""
    ab = abs(b)
    return (b * b / 10) * (5 - 2 * ab) if ab <= 1 else 1 - 1 / ab + 3 / (10 * ab * ab)


def tau_from_b(b: float) -> float:
    """Kendall’s τ(C_b) – odd in b."""
    if b >= 0:
        return (b * (4 - b)) / 6 if b <= 1 else (6 * b * b - 4 * b + 1) / (6 * b * b)
    return -tau_from_b(-b)


xi_vec, tau_vec = map(np.vectorize, (xi_from_b, tau_from_b))


# ----------------------------------------------------------------------
#  Main driver
# ----------------------------------------------------------------------
def main() -> None:
    # ---------------- Parameter grid (positive branch) ----------------
    b_pos = np.hstack(
        [
            np.linspace(0.0, 1.0, 600, endpoint=False)[1:],  # fine mesh 0<b≤1
            np.linspace(1.0, 20.0, 1400),  # stretch to large b
        ]
    )
    xi_pos, tau_pos = xi_vec(b_pos), tau_vec(b_pos)

    # Sort the positive branch by ξ so fill_between works monotonically
    sort_idx = np.argsort(xi_pos)
    xi_sorted = xi_pos[sort_idx]
    tau_sorted_pos = tau_pos[sort_idx]

    # -------------------------- Plotting ------------------------------
    BLUE, FILL = "#00529B", "#D6EAF8"
    fig, ax = plt.subplots(figsize=(8, 6))

    # Envelope curve ±τ(ξ) including the ceiling segments out to |τ|=1
    xi_plot = np.concatenate([xi_sorted, [1.0]])
    tau_plot_pos = np.concatenate([tau_sorted_pos, [1.0]])
    ax.plot(xi_plot, tau_plot_pos, color=BLUE, lw=2.5, label=r"$\pm\tau(\xi)$")
    ax.plot(xi_plot, -tau_plot_pos, color=BLUE, lw=2.5)

    # Fill attainable region
    ax.fill_between(
        xi_plot,
        -tau_plot_pos,
        tau_plot_pos,
        color=FILL,
        alpha=0.7,
        zorder=0,
        label="Attainable region",
    )

    # ---------------------- Highlight key points ----------------------
    # b0 = (10 - sqrt(10)) / 9  # ≈ 0.759
    # xi0 = xi_from_b(b0)
    # tau0 = tau_from_b(b0)

    # key_xi = [0, 1, 1, xi0, xi0]
    # key_tau = [0, 1, -1, tau0, -tau0]
    # ax.scatter(key_xi, key_tau, s=60, color="black", zorder=5)

    # Labels
    # ax.annotate(
    #     r"$\Pi$",
    #     (0, 0),
    #     xytext=(20, 0),
    #     textcoords="offset points",
    #     fontsize=18,
    #     ha="left",
    #     va="center",
    # )
    # ax.annotate(
    #     r"$M$",
    #     (1, 1),
    #     xytext=(0, -20),
    #     textcoords="offset points",
    #     fontsize=18,
    #     ha="center",
    #     va="top",
    # )
    # ax.annotate(
    #     r"$W$",
    #     (1, -1),
    #     xytext=(0, 20),
    #     textcoords="offset points",
    #     fontsize=18,
    #     ha="center",
    #     va="bottom",
    # )
    # ax.annotate(
    #     r"$C_{b_0}$",
    #     (xi0, tau0),
    #     xytext=(5, 0),
    #     textcoords="offset points",
    #     fontsize=18,
    #     ha="left",
    #     va="center",
    # )
    # ax.annotate(
    #     r"$C_{-b_0}$",
    #     (xi0, -tau0),
    #     xytext=(-5, 0),
    #     textcoords="offset points",
    #     fontsize=18,
    #     ha="right",
    #     va="center",
    # )

    # -------------------- Axes, grid, legend --------------------------
    ax.set_xlabel(r"Chatterjee's $\xi$", fontsize=16)
    ax.set_ylabel(r"Kendall's $\tau$", fontsize=16)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_aspect("equal", adjustable="box")
    ax.xaxis.set_major_locator(MultipleLocator(0.25))
    ax.yaxis.set_major_locator(MultipleLocator(0.25))
    ax.tick_params(labelsize=13)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.axhline(0, color="black", lw=0.8)

    # ax.legend(loc="upper center", fontsize=12, frameon=True)
    fig.tight_layout()
    pathlib.Path("images/").mkdir(parents=False, exist_ok=True)
    plt.savefig("images/xi-tau-region.png")
    plt.show()


if __name__ == "__main__":
    main()
