echo Build the shared library
clang -dynamiclib C/src/Python.c C/NDTable/src/Core.c C/NDTable/src/Interpolation.c -IC/include -IC/NDTable/include -o sdf/darwin64/libNDTable.dylib

echo List exported symbols
nm -gU sdf/darwin64/libNDTable.dylib

echo Build the distribution archive
python setup.py sdist
