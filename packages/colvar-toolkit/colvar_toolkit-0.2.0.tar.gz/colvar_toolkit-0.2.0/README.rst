PLUMED colvar
******************

A Python package to read and write PLUMED colvar files.

* Free software: MIT license

Installation
-----------------
You can either install via pip:

.. code-block:: bash

    pip install colvar-toolkit

Or install from the repository:

.. code-block:: bash

    pip install git+https://github.com/k9cdt/colvar-toolkit.git

Example usage
-----------------

Basic read/write operations:

.. code-block:: python

    from cvtoolkit import Colvar

    # Read a colvar file
    cv = Colvar.from_file('colvar.dat')

    # Access data
    bias = cv["metad.bias"]
    cv["metad.rct"] = my_array
    del cv["metad.acc"]

    # Write a new colvar file
    cv.write('new_colvar.dat')

Joining two files, and column-wise actions:

.. code-block:: python

    cv1 = Colvar.from_file('colvar1.dat')
    cv2 = Colvar.from_file('colvar2.dat')
    cv3 = Colvar.from_file('colvar3.dat').choose("rmsd")

    # Append time-wise
    # Throws an error if cv2 does not have all keys in cv1
    cv1.tappend(cv2)

    # Append key-wise
    # Throws an error if number of rows don't match
    cv1.kappend(cv3)