TQEC circuit generator
==============
This program is a generator for TQEC (Topologically Quantum Error-collected) circuit.

Requirements
---------------
* g++ 6.3 or later
* [CMake][cmake] 3.2 or later
* Python 3.4 or later
* sympy
* numpy
* docopt

How to build
---------------
```
$ cd build
$ cmake ..
$ make
```

How to use
---------------
```
# generate TQEC circuit modules from a icpm template circuit
# the default circuit is 'cv'
$ ./main.py [-t | --type <type>] [-e | --error <error>] [-s | --size <size>]

# convert a json file format
$ ./main.py convert <format> <file>

# show help
$ ./main.py -h | --help
```

[cmake]: https://cmake.org/
