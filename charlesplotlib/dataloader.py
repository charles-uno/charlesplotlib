# Charles McEachern

# Summer 2016

# ######################################################################
# ############################################################# Synopsis
# ######################################################################

# This file defines the `readarray` function, which takes one argument,
# the name of a text file. A Numpy array of the file's contents is
# returned, and also stored as a pickle so that the data can be read in
# faster next time. The first line of the file should give the array
# dimensions (as integers, separated by whitespace). The rest of the
# file is then read in as floats or Fortran-style complexes to fill that
# array. 

# ######################################################################
# ############################################################## Imports
# ######################################################################

import numpy as np

import os

import time

try:
  import cPickle as pickle
except ImportError:
  import pickle

from . import helpers








class DataLoader(object):
    """This object is used for accessing Tuna's output. It keeps track
    of the location of the data files, knows which directories
    correspond to runs with what input parameters, and delivers arrays
    based on those parameters.
    """
    # A dictionary of parameter dictionaries, keyed by data path. 
    pathparams = None
    # Keep track of a handful of recent arrays we've read in. 
    memory = None

    # ==================================================================

    def __init__(self, *args):
        """Given one or more directory paths, find all subdirectories
        containing Tuna output. File input parameters by data path. 
        """
        self.pathparams = {}
        stopwatch = time.time()
        print('Loading data parameters...', end='')
        # Walk recursively through each data directory. Parse the
        # parameter input file for any folder that has one.
        for datapath in args:
            for root, dirs, files in os.walk(datapath):
                lines = helpers.read( os.path.join(root, 'params.in') )
                # If there's no input, this is not a data directory. 
                if lines is None:
                    continue
                # Set up a dictionary entry for each data directory. 
                # Entries within that dictionary are themselves
                # dictionaries, holding the parameters from that run. 
                # Add default parameter values to make searching easier.
                self.pathparams[root] = { 'bdrive':0, 'jdrive':0,
                                          'inertia':-1, 'fdrive':0.016,
                                          'azm':0, 'n1':150, 'lpp':4,
                                          'ldrive':5}
                for k, v in [ x.split('=') for x in lines ]:
                    self.pathparams[root][ k.strip() ] = helpers.num(v)
        # Report what all we got, and how long it took. 
        print( 'Loaded parameters for', len(self.pathparams),
               'directories in', format(time.time() - stopwatch, '.1f'),
               'seconds.')
        return

    # ==================================================================

    def get_path(self, **kwargs):
        """Get the data path matching the given keyword arguments."""
        match = None
        for path, params in self.pathparams.items():
            # For each path, check against all keyword arguments. As
            # soon as we find a mismatch, bail. 
            for key, val in kwargs.items():
                if key not in params or params[key] != val:
                    break
            # If we find them all to match, keep track of this path. 
            else:
                if match is None:
                    match = path
                # If we find multiple matches, complain. 
                else:
                    raise ValueError( 'Multiple paths matching ' +
                                      str(kwargs) + '.' )
        # If, after iterating through all of the paths, we have no
        # matches, complain. 
        if match is None:
            raise ValueError('No paths matching ' + str(kwargs) + '.')
        else:
            return match

    # ==================================================================

    def get_array(self, path, name):
        """Read in an array. Keep track of the most recent arrays to
        avoid wasting time on duplicate reads of the same file. 
        """
        filename = os.path.join(path, name + '.dat')
        # Set the memory on the first call, or reset it if it's full. 
        if self.memory is None or len(self.memory) > 20:
            self.memory = {}
        # If we haven't read in this file, do so.
        if filename not in self.memory:
            self.memory[filename] = readarray(filename)
        return self.memory[filename]



# ######################################################################
# ############################################################## Helpers
# ######################################################################

def by(x):
    """Turns a list of numbers (1, 2, 3) into the string '1x2x3'."""
    if len(x) == 1:
        return str( x[0] )
    else:
        return str( x[0] ) + 'x' + by( x[1:] )

# ----------------------------------------------------------------------

def com(x):
    """Convert a string into a complex or float."""
    # If there's a comma, it's a complex number expressed in the form
    # '(real, imag)'. 
    if ',' in x:
        real, imag = x[1:-1].split(',')
        return (float(real) + float(imag)*1j)
    # Otherwise, it's a float. 
    else:
        return float(x)

# ######################################################################
# ######################################################### Array Reader
# ######################################################################

def readarray(filename):
    """Read a file of values into an array. We expect the first line to
    give the array dimensions. The rest of the file should just be real
    or complex numbers, and is agnostic to whitespace and newlines.
    """
    # Shave off the file extension, and get names for the text data file
    # (dat) and pickled data (pkl). 
    name = filename[ :filename.rfind('.') ]
    datname, pklname = name + '.dat', name + '.p3'
    # Keep track of how long this takes. It might be a while. 
    stopwatch = time.time()
    # If a pickle is available, read that. 
    if os.path.isfile(pklname):
        print('Reading:', pklname, '...', end='')
        with open(pklname, 'rb') as handle:
            arr = pickle.load(handle)
    # If there's no pickle, parse the Fortran output. 
    elif os.path.isfile(datname):
        print('Reading:', datname, '...', end='')
        # Grab the data as a list of strings. 
        with open(datname, 'r') as handle:
            datlines = handle.readlines()
        # The first line gives array dimensions. 
        dims = [ int(x) for x in datlines.pop(0).split() ]
        size = np.prod(dims)
        # Assemble a one-dimensional array large enough to hold all the
        # values -- this is much faster than appending as we go. Check
        # for a comma to see if we're dealing with floats or complexes.
        if len(datlines) > 0 and ',' in datlines[0]:
            flatarr = np.empty(size, dtype=np.complex)
        else:
            flatarr = np.empty(size, dtype=np.float)
        # Fill the array with values one at a time. Stop when it's full,
        # or when we run out of values. 
        i = 0
        for line in datlines:
            for x in line.split():
                # Check if the array is full. 
                if i == size:
                    break
                # If it's not, grab the next value. 
                else:
                    flatarr[i] = com(x)
                    i += 1
        # Reshape and transpose the array. Fortran and Python have
        # opposite indexing conventions. 
        arr = np.transpose( np.reshape( flatarr, dims[::-1] ) )
        # Check the array dimensions. If it's not full, the run may have
        # crashed. Return what exists, but print a warning. 
        actualdims = dims[:-1] + [ np.int( i/np.prod(dims[:-1]) ) ]
        if dims != actualdims:
            print('INCOMPLETE!', '...', end='')
            arr = arr[ ..., :actualdims[-1] ]
        # Create a pickle for next time. 
        print('PICKLING!', '...', end='')
        with open(pklname, 'wb') as handle:
            pickle.dump(arr, handle, protocol=-1)
    # If the data is missing, bail. 
    else:
        raise RuntimeError( 'File not found:' + str(filename) )
    # Print off what we got and how long it took. 
    dt = format(time.time() - stopwatch, '5.1f') + 's'
    print(by(arr.shape), '...', dt)
    # Finally, return the array! 
    return arr










