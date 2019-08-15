# pyauric #

pyauric is a standalone package I made for interfacing with CPI's AURIC model from inside python functions and ipython notebooks. Install it using,

    cd pyauric
    python setup.py install

or, even better, use the `develop` option to stay up-to-date with changes without reinstalling.

    cd pyauric
    python setup.py develop

There is a basic test to check that the environment makes sense. Run it with

	python setup.py test

### What is this repository for? ###

* Interface with the AURIC model from python
* Change `param.inp` or `radtrans.opt` from a dictionary
* Read AURIC output into pandas DataFrames
* maybe other neat things in the future!

### Dependencies ###

* python 3.3 or later
* fortranformat
* numpy
* pandas
* matplotlib (optional)


### Contribution guidelines ###

This code uses regular expressions to parse fortran records. 
This is mostly due to laziness and reluctance to learn how to use FortranRecordReader properly.
It parses all of the files I have tried correctly, but if you find an error, please contribute a solution.
