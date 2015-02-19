# pyauric #

pyauric is a standalone package I made for interfacing with CPI's AURIC model from inside python functions and ipython notebooks. Install it using,

    cd pyauric
    python setup.py install

or, even better, use the `develop` option to stay up-to-date with changes without reinstalling.

    cd pyauric
    python setup.py develop

### What is this repository for? ###

* Interface with the AURIC model without using the icky fortran menu
* Change `param.inp` or `radtrans.opt` from a dictionary
* Read AURIC output into numpy arrays
* maybe other neat things in the future!

### Dependencies ###

* standard python stuff

### Contribution guidelines ###

This code uses regular expressions to parse fortran records. 
This is mostly due to laziness and reluctance to learn how to use FortranRecordReader properly.
It parses all of the files I have tried correctly, but if you find an error, please contribute a solution.
