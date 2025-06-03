"""
Spline based interpolation methods
"""

import numpy as np
import matplotlib.pyplot as plt
from sdf.ndtable import NDTable


x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([0, 1, 2, 2, 3, 4])

table = NDTable(y, (x,))

xi = np.linspace(-1, 6, 1000)
dxi = np.ones_like(xi)


methods = ["akima", "fritsch-butland", "steffen"]

figure, axes = plt.subplots(len(methods), sharex=True)

figure.set_facecolor("white")

for ax, method in zip(axes, methods):
    yi = table.evaluate((xi,), interp=method, extrap="linear")
    dyi = table.evaluate_derivative((xi,), (dxi,), interp=method, extrap="linear")
    ax.set_title(method)
    ax.grid(True, color="0.9")
    ax.plot(x, y, "or", label="samples", zorder=300)
    ax.plot(xi, yi, "b", label="interpolated", zorder=100)
    ax.plot(xi, dyi, "r", label="derivative", zorder=100)
    ax.margins(x=0, y=0.1)

plt.legend(
    bbox_to_anchor=(0, -0.75, 1.0, 0.1), loc=8, ncol=3, mode="normal", borderaxespad=0.5
)

figure.tight_layout()
figure.subplots_adjust(bottom=0.18, hspace=0.5)
plt.show()
