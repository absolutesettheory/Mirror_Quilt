#!/usr/bin/env python3
"""
Asset Generator for Mirror-Quilt Framework (v3.0)
Author: Christopher Thomas Ronio

Generates Mirror_Quilt_and_Twist.png (Figure 1) and Mirror_Quilt_3D.png (Figure 2)
inside the repository's assets/ directory.
"""

import os
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("../assets", exist_ok=True)

# --- Figure 1: 2D Quilt & Möbius/Spin-Sweep Twist ---
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_facecolor("#111111")
fig.patch.set_facecolor("#1b1b1b")

# Draw a 4x4 checkerboard grid representing absolute finite cells
for i in range(-2, 3):
    for j in range(-2, 3):
        color = "#2a2a2a" if (i + j) % 2 == 0 else "#383838"
        rect = plt.Rectangle((i, j), 1, 1, facecolor=color, edgecolor="#555555")
        ax.add_patch(rect)
        ax.text(
            i + 0.5,
            j + 0.5,
            f"det={'+' if (i+j)%2==0 else '-'}",
            color="#aaaaaa",
            fontsize=8,
            ha="center",
            va="center",
        )

# Draw Spin-Sweep trajectory loop
theta = np.linspace(0, 2 * np.pi, 200)
x_loop = 0.5 + 1.5 * np.cos(theta)
y_loop = 0.5 + 1.5 * np.sin(theta)
ax.plot(
    x_loop, y_loop, color="#00ffcc", lw=2, label="Spin-Sweep Path S(theta)"
)

ax.set_xlim(-2.5, 3.5)
ax.set_ylim(-2.5, 3.5)
ax.axhline(0, color="#777777", ls="--")
ax.axvline(0, color="#777777", ls="--")
ax.set_title(
    "Figure 1: Mirror-Quilt Checkerboard & Spin-Sweep Loop", color="white"
)
ax.legend(loc="upper right", facecolor="#222222", edgecolor="none", labelcolor="white")
plt.tight_layout()
plt.savefig("../assets/Mirror_Quilt_and_Twist.png", dpi=300)
plt.close()

# --- Figure 2: 3D Handedness Triads & Boundary Planes ---
fig = plt.figure(figsize=(7, 6))
ax = fig.add_subplot(projection="3d")
fig.patch.set_facecolor("#1b1b1b")
ax.set_facecolor("#111111")

# Draw unit cell C(0,0,0) and C(1,0,0)
r = [0, 1]
for x in r:
    for y in r:
        ax.plot([x, x], [y, y], [0, 1], color="#00ffcc", alpha=0.6)
        ax.plot([x, x], [0, 1], [y, y], color="#00ffcc", alpha=0.6)
        ax.plot([0, 1], [x, x], [y, y], color="#00ffcc", alpha=0.6)

ax.text(0.5, 0.5, 0.5, "Cell C(0,0,0)\ndet = +1", color="white", fontsize=9, ha="center")
ax.text(1.5, 0.5, 0.5, "Cell C(1,0,0)\ndet = -1 (Axiom 4)", color="#ff5555", fontsize=9, ha="center")

# Shifted cell for contrast
for x in [1, 2]:
    for y in r:
        ax.plot([x, x], [y, y], [0, 1], color="#ff55ff", alpha=0.4)

ax.set_title("Figure 2: Affine Reflection Group Lattice ($D_\\infty^3$)", color="white")
ax.xaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))
ax.yaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))
ax.zaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))

plt.savefig("../assets/Mirror_Quilt_3D.png", dpi=300)
plt.close()

print("Successfully generated assets/Mirror_Quilt_and_Twist.png and assets/Mirror_Quilt_3D.png!")
