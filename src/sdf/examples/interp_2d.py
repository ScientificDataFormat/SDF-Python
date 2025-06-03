"""
2d interpolation example
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import NonUniformImage
from sdf.ndtable import NDTable


def peaks(x=np.linspace(-3, 3, 49), y=np.linspace(-3, 3, 49)):
    X, Y = np.meshgrid(x, y)
    Z = (
        3 * (1 - X) ** 2 * np.e ** (-(X**2) - (Y + 1) ** 2)
        - 10 * (X / 5 - X**3 - Y**5) * np.e ** (-(X**2) - Y**2)
        - 1 / 3 * np.e ** (-((X + 1) ** 2) - Y**2)
    )
    return X, Y, Z


x = y = np.linspace(-3, 3, 15)
_, _, Z = peaks(x, y)
table = NDTable(Z, (x, y))

xi = yi = np.linspace(-6, 6, 200)
XI, YI = np.meshgrid(xi, yi, indexing="ij")

figure, axes = plt.subplots(ncols=2, nrows=2, sharex=True, sharey=True)
figure.set_facecolor("white")

axes = axes.flatten()

ax = axes[0]
ax.set_title("original")
im = NonUniformImage(ax)
im.set_data(x, y, Z)
im.set_extent((-3, 3, -3, 3))
ax.add_image(im)
ax.set_xlim([-6, 6])
ax.set_ylim([-6, 6])

methods = [("nearest", "hold"), ("linear", "linear"), ("akima", "linear")]

for ax, method in zip(axes[1:], methods):
    ZI = table.evaluate((XI, YI), interp=method[0], extrap=method[1])
    ax.set_title("interp='%s', extrap='%s'" % method)
    im = NonUniformImage(ax)
    im.set_data(xi, yi, ZI)
    im.set_extent((-6, 6, -6, 6))
    ax.add_image(im)

figure.tight_layout()
plt.show()
