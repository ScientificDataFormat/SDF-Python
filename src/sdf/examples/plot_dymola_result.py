import sdf
import matplotlib.pyplot as plt


# the Dymola result file
filename = "IntegerNetwork1.mat"

# model variables to plot
variables = ["sum.y", "product.y", "triggeredAdd.y", "multiSwitch1.y"]

datasets = []

for variable in variables:
    # convert the Modelica path to an absolute SDF/HDF5 path
    path = "/" + variable.replace(".", "/")
    # read the dataset
    datasets.append(sdf.load(filename, path))

# plot the datasets
figure, ax = plt.subplots()

for dataset, variable in zip(datasets, variables):
    ax.plot(dataset.scales[0].data, dataset.data, label=variable)

ax.legend()
plt.show()
