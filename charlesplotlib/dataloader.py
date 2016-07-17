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


import .helpers







class DataLoader(object):
    """This object is used for accessing Tuna's output. It keeps track
    of the location of the data files, knows which directories
    correspond to runs with what input parameters, and delivers arrays
    based on those parameters.
    """
    # A dictionary of parameter dictionaries, keyed by data path. 
    pathparams = {}

    # ==================================================================

    def __init__(self, datapath):
        """Find all the directories containing Tuna output and file them
        in terms of their run parameters.
        """
        stopwatch = time.time()
        print('Loading data parameters...', end='')
        # Walk recursively through the data directory. Parse the
        # parameter input file for any folder that has one.
        for root, dirs, files in os.walk(datapath):
            paramlines = read( os.path.join(root, 'params.in') )
            # If there's no input file, this is not a data directory. 
            if paramlines is None:
                continue
            # Set up a dictionary entry for each data directory. Entries
            # within that dictionary are themselves dictionaries,
            # keeping track of the parameters for that run. 
            self.pathparams[root] = {}
            for key, val in [ x.split('=') for x in paramlines ]:
                self.pathparams[root][ key.strip() ] = num(val)
        # Report what all we got, and how long it took. 
        print( 'Loaded parameters for', len(self.pathparams),
               'directories in', format(time.time() - stopwatch, '.1f'),
               'seconds.')
        return
        
    # ==================================================================














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



'''

  def getPath(self, **kargs):
    # Start with all the paths we have, then weed out any that don't match. 
    paths = [ p for p in self.paths ]
    for key, val in kargs.items():
      paths = [ p for p in paths if self.paths[p][key]==val ]
    # If there's anything other than exactly one match, something is wrong. 
    if len(paths)<1:
      print 'WARNING: No matching path found for ', kargs
      return None
    elif len(paths)>1:
      print 'ERROR: Multiple matching paths found for ', kargs
      exit()
    else:
      return paths[0]

'''


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
    datname, pklname = name + '.dat', name + '.pkl'
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
            flatarr = np.empty(size, dtyle=np.complex)
        else:
            flatarr = np.empty(size, dtyle=np.float)
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










