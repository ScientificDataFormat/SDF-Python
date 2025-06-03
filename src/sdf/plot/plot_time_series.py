import sdf
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pylab as pylab


def plot_time_series(filename, datasets):
    params = {
        # 'legend.fontsize': 'medium',
        "figure.figsize": (10, 8),
        "axes.labelsize": "small",
        #   'axes.titlesize': 'medium',
        "xtick.labelsize": "small",
        "ytick.labelsize": "small",
    }

    pylab.rcParams.update(params)

    figure, axes = plt.subplots(len(datasets), sharex=True)

    # figure = plt.figure()
    figure.patch.set_facecolor("white")

    for ax, path in zip(axes, datasets):
        dataset = sdf.load(filename, path)

        scale = dataset.scales[0]

        y = dataset.data
        x = scale.data if scale is not None else range(len(y))

        # ax = figure.add_subplot(len(datasets), 1, i + 1)

        ax.plot(x, y, "b")

        ax.grid(b=True, which="both", color="0.8", linestyle="-")

        ax.set_xlim([np.nanmin(x), np.nanmax(x)])
        ylabel = path
        if dataset.unit is not None:
            ylabel += " / %s" % dataset.unit
        ax.set_ylabel(ylabel)
        ax.margins(y=0.05)

    # x-axis label
    if scale is not None:
        xlabel = scale.name
        if scale.unit is not None:
            xlabel += " / %s" % scale.unit
        else:
            xlabel = "Index"
        ax.set_xlabel(xlabel)

    figure.tight_layout()

    plt.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("datasets", nargs="+")
    args = parser.parse_args()

    plot_time_series(filename=args.filename, datasets=args.datasets)
