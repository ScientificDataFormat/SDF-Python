from distutils.core import setup

setup(name="sdf",
      version="0.3.1",
      description="Scientific Data Format",
      url="",
      author="",
      author_email="",
      license="Standard 3-clause BSD",
      packages=["sdf", "sdf.examples", "sdf.plot"],
      package_data={"sdf": ["examples/IntegerNetwork1.mat", "win32/ndtable.dll", "win64/ndtable.dll", "linux64/libndtable.so", "darwin64/libNDTable.dylib"]},
      long_description="""A Python library to read and write SDF files and to interpolate multi-dimensional data""",
      platforms=["win32", "win64", "linux64", "darwin64"])
