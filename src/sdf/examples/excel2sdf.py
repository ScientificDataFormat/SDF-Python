"""
Import data from an Excel sheet to SDF
"""

import os.path
import xlrd
from numpy import array
import sdf


# name of the Excel file to import
filename = "time_series.xlsx"

# open the workbook
book = xlrd.open_workbook(filename)

# get the first sheet
sh = book.sheet_by_index(0)

# get the names, quantities and units
n_t = sh.cell_value(0, 1)
u_t = sh.cell_value(1, 1)

n_u = sh.cell_value(0, 2)
u_u = sh.cell_value(1, 2)

# get the data
col_t = sh.col_values(1, 2, sh.nrows)
col_u = sh.col_values(2, 2, sh.nrows)

# create the data arrays
t = array(col_t)
u = array(col_u)

# create the datasets
ds_t = sdf.Dataset(n_t, data=t, unit=u_t, is_scale=True, display_name="Time")
ds_u = sdf.Dataset(n_u, data=u, unit=u_u, scales=[ds_t])

# create the root group
g = sdf.Group("/", comment="Imported from " + filename, datasets=[ds_t, ds_u])

# change the file extension
outfile = os.path.splitext(filename)[0] + ".sdf"

# write the SDF file
sdf.save(outfile, g)
