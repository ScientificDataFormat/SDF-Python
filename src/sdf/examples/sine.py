"""
Create a simple SDF file
"""

import sdf
import numpy as np

# create the data arrays
t = np.linspace(0, 10, 100)
v = np.sin(t)

# create the datasets
ds_t = sdf.Dataset("t", data=t, unit="s", is_scale=True, display_name="Time")
ds_v = sdf.Dataset("v", data=v, unit="V", scales=[ds_t])

# create the root group
g = sdf.Group("/", comment="A sine voltage", datasets=[ds_t, ds_v])

# write the SDF file
sdf.save("sine.sdf", g)

# read the SDF file
ds_v2 = sdf.load("sine.sdf", "/v", unit="V", scale_units=["s"])
ds_t2 = ds_v2.scales[0]

t2 = ds_t2.data
v2 = ds_v2.data
