TQEC
==============
This program is ~.

Requirements
---------------
* g++ 4.9 or later
* [CMake][cmake] 3.3 or later
* Python 3.4 or later
* LAPACK
* BLAS

How to build
---------------
```
$ cd build
$ cmake [-DCMAKE_BUILD_TYPE=(Debug|Release)] ..
$ make
```

How to use
---------------
```
# Try to merge gates in a circuit. Using esop minimization of ABC.
# Default test data are blif or pla files in 'test_data' directory.
$ ./main.py [*.(blif|pla)]

# Try to merge gates in a circuit.
# A default test data is 'test_data/alu4.esop'.
$ ./bin/merging [*.(qo|esop)]

# Show groups.
# A default test data is 'test_data/alu4.esop'.
$ ./bin/grouping [*.(qo|esop)]

# Covert esop to qo and show number of gates.
# A default test data is 'test_data/alu4.esop'.
$ ./bin/esop_to_qo [*.esop]

# Show circuit's cost.
# A default test data is 'test_data/alu4.esop'.
$ ./bin/print_cost [*.(qo|esop)]
```

[cmake]: https://cmake.org/
[qc]: https://github.com/rxnew/qc
[qc_ver]: https://github.com/rxnew/qc/releases/tag/v1.4.8.1
