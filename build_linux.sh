echo Build the shared library
gcc -c -Wall -Werror -fpic -IC/include -IC/NDTable/include C/src/Python.c
gcc -c -Wall -Werror -fpic -IC/NDTable/include C/NDTable/src/Core.c
gcc -c -Wall -Werror -fpic -IC/NDTable/include C/NDTable/src/Interpolation.c
gcc -shared -o sdf/linux64/libNDTable.so Python.o Core.o Interpolation.o

echo List exported symbols
nm -g sdf/linux64/libndtable.so

echo Build the distribution archive
python setup.py sdist
