"""
Interpolation Methods
"""

import numpy as np
import matplotlib.pyplot as plt
from sdf.ndtable import NDTable

x = np.linspace(0, 2 * np.pi, 6)
y = np.sin(x)

table = NDTable(y, (x,))

xi = np.linspace(-1.5, 2 * np.pi + 1.5, 1000)
dxi = np.ones_like(xi)

methods = [
    ("hold", "hold"),
    ("nearest", "hold"),
    ("linear", "linear"),
    ("akima", "linear"),
]

figure, axes = plt.subplots(len(methods), sharex=True)

figure.set_facecolor("white")

for ax, method in zip(axes, methods):
    yi = table.evaluate((xi,), interp=method[0], extrap=method[1])
    dyi = table.evaluate_derivative((xi,), (dxi,), interp=method[0], extrap=method[1])
    ax.set_title("interp='%s', extrap='%s'" % method)
    ax.grid(True, color="0.9")
    ax.plot(x, y, "or", label="samples", zorder=300)
    ax.plot(xi, yi, "b", label="interpolated", zorder=100)
    ax.plot(xi, dyi, "r", label="derivative", zorder=100)
    ax.set_xlim([-1.5, 2 * np.pi + 1.5])
    ax.set_ylim([-2, 2])

plt.legend(
    bbox_to_anchor=(0, -0.75, 1.0, 0.1), loc=8, ncol=3, mode="normal", borderaxespad=0.5
)

figure.set_size_inches(w=8, h=8, forward=True)
figure.tight_layout()
figure.subplots_adjust(bottom=0.15, hspace=0.5)
plt.show()
