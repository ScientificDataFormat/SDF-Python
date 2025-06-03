"""
Create a contour plot from an SDF dataset
"""

import numpy as np
import sdf
import sys
import matplotlib.pyplot as plt


filename = sys.argv[1]
objects = sys.argv[2]

dataset = sdf.load(filename, objects)

delta = 0.025


x = dataset.scales[1].data
y = dataset.scales[0].data

subs = [0] * dataset.data.ndim
subs[0] = slice(None)
subs[1] = slice(None)

Z = dataset.data[subs].T

X, Y = np.meshgrid(x, y, indexing="ij")

figure = plt.figure()

figure.patch.set_facecolor("white")

ax = figure.add_subplot(1, 1, 1)

ax.grid(True)

CS = plt.contourf(X, Y, Z, 10, cmap=plt.cm.viridis)

cbar = figure.colorbar(CS)

CS = plt.contour(X, Y, Z, 10, colors="k")

plt.clabel(CS=CS, fontsize=9, inline=1, colors="k")

ax.set_title(dataset.display_name + " / " + dataset.unit)
ax.set_xlabel(dataset.scales[1].display_name + " / " + dataset.scales[1].unit)
ax.set_ylabel(dataset.scales[0].display_name + " / " + dataset.scales[0].unit)

plt.tight_layout()

plt.show()
