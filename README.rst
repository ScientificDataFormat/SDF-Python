.. image:: https://ci.appveyor.com/api/projects/status/github/ScientificDataFormat/SDF-Python?branch=master


Scientific Data Format for Python
=================================

SDF is a Python package to read, write and interpolate multi-dimensional data.
The Scientific Data Format is an open file format based on HDF5_ to store
multi-dimensional data such as parameters, simulation results or measurements.
It supports...

- very large files
- up to 32 dimensions
- hierarchical structure
- units, comments and custom meta-information

For detailed information see the `SDF specification`_.


Installation
------------

To install the latest release from `PyPI <https://pypi.python.org/pypi/sdf/>`_ or update an existing installation::

    python -m pip install --upgrade sdf

To install the latest development version::

    python -m pip install --upgrade https://github.com/ScientificDataFormat/SDF-Python/archive/develop.zip


Tutorial
--------

Import the ``SDF`` and ``NumPy`` packages:

    >>> import sdf
    >>> import numpy as np

Create the data arrays:

    >>> t = np.linspace(0, 10, 51)
    >>> v = np.sin(t)

Create the datasets:

    >>> ds_t = sdf.Dataset('t', data=t, unit='s', is_scale=True, display_name='Time')
    >>> ds_v = sdf.Dataset('v', data=v, unit='V', scales=[ds_t])

Create the root group and write the file:

    >>> g = sdf.Group('/', comment='A sine voltage', datasets=[ds_t, ds_v])
    >>> sdf.save('sine.sdf', g)

Read the dataset from the SDF file asserting the correct unit of the dataset and scale:

    >>> ds_v2 = sdf.load('sine.sdf', '/v', unit='V', scale_units=['s'])

Get the meta info and data array from the dataset:

    >>> ds_v2.unit
    'V'
    >>> ds_v2.data.shape
    (51,)

Get the scale for the first dimension:

    >>> ds_t2 = ds_v2.scales[0]
    >>> ds_t2.unit
    's'


-----------------------------

|copyright| 2017 |Dassault Systemes|

.. _SDF specification: https://github.com/ScientificDataFormat/SDF
.. _HDF5: https://www.hdfgroup.org/hdf5/
.. |copyright|   unicode:: U+000A9
.. |Dassault Systemes| unicode:: Dassault U+0020 Syst U+00E8 mes
