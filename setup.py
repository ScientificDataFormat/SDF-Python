from setuptools import setup


def readme():
    """ Get the content of README.rst without the CI badges """
    with open('README.rst') as f:
        lines = f.readlines()
        while not lines[0].startswith("Scientific Data Format"):
            lines = lines[1:]
        return ''.join(lines)


setup(name='SDF',
      version='0.3.5',
      description="Work with Scientific Data Format files in Python",
      long_description=readme(),
      url="https://github.com/ScientificDataFormat/SDF-Python",
      author="Torsten Sommer",
      author_email='torsten.sommer@3ds.com',
      license="Standard 3-clause BSD",
      packages=['sdf', 'sdf.examples', 'sdf.plot'],
      package_data={'sdf': ['examples/IntegerNetwork1.mat',
                            'win32/ndtable.dll',
                            'win64/ndtable.dll',
                            'linux64/libndtable.so',
                            'darwin64/libNDTable.dylib']},
      platforms=['darwin64', 'linux64', 'win32', 'win64'],
      install_requires=['numpy>=2', 'h5py', 'matplotlib', 'scipy'])
