"""
Create a contour plot from an SDF dataset
"""

import numpy as np
import sdf
import matplotlib.pyplot as plt
from matplotlib import colors

import matplotlib.pylab as pylab


def create_plot(filename, datasets):
    params = {
        # 'legend.fontsize': 'medium',
        # 'figure.figsize': (10, 8),
        "legend.fontsize": "small",
        "axes.labelsize": "small",
        "axes.titlesize": "small",
        "xtick.labelsize": "small",
        "ytick.labelsize": "small",
    }

    pylab.rcParams.update(params)

    figure = plt.figure(figsize=(12, 8))
    figure.patch.set_facecolor("white")

    for row, dataset in enumerate(datasets):
        # load the datasets
        C1 = sdf.load(filename, dataset)

        ncols = C1.scales[2].data.size

        norm = colors.Normalize(vmin=np.nanmin(C1.data), vmax=np.nanmax(C1.data))

        subs = [0] * C1.data.ndim
        subs[0] = slice(None)
        subs[1] = slice(None)

        ax0 = None

        for i in range(ncols):
            x = C1.scales[1].data
            y = C1.scales[0].data

            subs[2] = i

            Z = C1.data[subs].T

            X, Y = np.meshgrid(x, y, indexing="ij")

            ax = figure.add_subplot(
                len(datasets),
                C1.data.shape[2],
                (row * ncols) + i + 1,
                sharex=ax0,
                sharey=ax0,
            )

            if i == 0:
                ax0 = ax
                ax.set_ylabel(
                    C1.display_name
                    + " / "
                    + C1.unit
                    + "\n"
                    + C1.scales[0].display_name
                    + " / "
                    + C1.scales[0].unit
                )
            # else:
            #     ax.get_yaxis().set_ticklabels([])

            ax.grid(True)

            CSF = plt.contourf(X, Y, Z, 10, cmap=plt.cm.viridis, norm=norm)

            CS = plt.contour(X, Y, Z, 10, colors="k")

            plt.clabel(CS=CS, fontsize=9, inline=1, colors="k")

            scale3 = C1.scales[2]

            ax.set_title(
                scale3.display_name + "=" + ("%g" % scale3.data[i]) + " " + scale3.unit
            )
            ax.set_xlabel(C1.scales[1].display_name + " / " + C1.scales[1].unit)

        figure.colorbar(CSF)

    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("datasets", nargs="+")
    args = parser.parse_args()

    create_plot(filename=args.filename, datasets=args.datasets)
