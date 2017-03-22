# Charles McEachern

# Summer 2016

# WIP...

# ######################################################################

import cubehelix
import matplotlib
import numpy as np
import os
# Allows use over SSH, even from a machine not running an xserver.
if 'DISPLAY' not in os.environ or os.environ['DISPLAY'] is '':
    matplotlib.use('Agg')
from matplotlib import gridspec, rc
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import LinearSegmentedColormap as lsc
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.colors import LogNorm, Normalize, SymLogNorm
from matplotlib.patches import Wedge
from time import localtime as lt

# ######################################################################

def num(x):
    """Attempt to cast a string as a float or integer. Failing that,
    return the string.
    """
    for typ in (int, float):
        try:
            return typ(x)
        except ValueError:
            pass
    return x

# ----------------------------------------------------------------------

def read(filename):
    """Return the contents of a text file as a list of right-stripped
    strings.
    """
    if os.path.isfile(filename):
        with open(filename, 'r') as handle:
            return [ x.rstrip() for x in handle ]
    else:
        return None

# ######################################################################
# ###################################################### Tick Formatters
# ######################################################################

def fmt_int(z):
    """Round a number to an integer and wrap it in dollar signs."""
    return '$' + str( int(z) ) + '$'

# ----------------------------------------------------------------------

def fmt_pow(z):
    """Format a number in the form '$10^{x}'."""
    if z == 0:
        return '$0$'
    else:
        return '$10^{' + format(np.log10(z), '.0f') + '}$'




# ######################################################################
# ########################################################### Color Maps
# ######################################################################

def div_cmap(ncolors=1024):
    """Create a diverging colormap using cubehelix."""
    # Get a high-resolution unit interval. Evaluate two cubehelixes on
    # it, one for the positive values and one for the negatives.
    u = np.linspace(0., 1., 1024)
    bot = cubehelix.cmap(start=0.5, rot=-0.5)(u)
    top = cubehelix.cmap(start=0.5, rot=0.5, reverse=True)(u)
    # Slap the two together into a linear segmented colormap.
    ch = lsc.from_list( 'ch_sym', np.vstack( (bot, top) ) )
    # From there, get a colormap with the desired number of intervals.
    return ListedColormap( ch( np.linspace(0.05, 0.95, ncolors) ) )

# ----------------------------------------------------------------------

def seq_cmap(ncolors=1024):
    """Create a sequential colormap using cubehelix."""
    ch = cubehelix.cmap(start=1.5, rot=-1, reverse=True)
    # Limit to a discrete number of color intervals.
    return ListedColormap( ch( np.linspace(0., 1., ncolors) ) )






# ######################################################################
# ##################################################### Helper Functions
# ######################################################################

def dslice(d, keys):
    """Takes a dictionary and a sequence of keys. Returns a new
    dictionary, containing only the entries of the original which match
    a given key.
    """
    return dict( (k, v) for k, v in d.items() if k in keys )

# ----------------------------------------------------------------------

def dsum(*args):
    """Combines several dictionary arguments, or each entry in a
    sequence or generator of dictionaries.
    """
    dlist = list( args[0] ) if len(args)==1 else args
    return dict( sum( [ list( d.items() ) for d in dlist ], [] ) )

# ----------------------------------------------------------------------



def flatten(*args):

    if len(args) == 0:
        return []

    elif len(args) == 1:
        # If given a generator, evaluate it into a list.
        l = list( args[0] )

    pass



def values(*args):
    """Take several arguments, or a single sequence or generator, and
    return a flattened list of values. None-valued entries are trimmed.
    """
    # No arguments.
    if len(args) == 0:
        return []
    elif len(args) == 1:
        # We're dealing with a list/generator full of numbers. Or maybe
        # full of arrays. Evaluate it, turn it into a (potentially
        # multidimensional) array, and flatten it to a list of numbers.
        temp = np.array( list( args[0] ) ).flatten()
        return np.array( [ x for x in temp if x is not None ] )
    else:
        # If given multiple arguments, assume they're numbers.

        # Safer would be to return sum( [ flatten([x]) for x in args ], [] ) with the None values pulled out.
        return [ x for x in  args if x is not None ]

# ----------------------------------------------------------------------

def nax(*args):
    """Get the maximum of a possibly-empty list or generator."""
    vals = values(*args)
    return np.max(vals) if len(vals) else None

# ----------------------------------------------------------------------

def ned(*args):
    """Get the median of a possibly-empty list or generator."""
    vals = values(*args)
    return np.median(vals) if len(vals) else None

# ----------------------------------------------------------------------

def nin(*args):
    """Get the minimum of a possibly-empty list or generator."""
    vals = values(*args)
    return np.min(vals) if len(vals) else None

# ----------------------------------------------------------------------

def notex(x):
    """Format a chunk of text to be non-math LaTeX."""
    if '\n' in x:
        # If there are multiple lines, handle each individually.
        return ' $ \n $ '.join( notex(y) for y in x.split('\n') )
    else:
        return '\\operatorname{' + x.replace(' ', '\\;') + '}'

# ----------------------------------------------------------------------

def tex(x):
    """Split a string into math and non-math chunks, by dollar signs."""
    nomath = x.split('$')[::2]
    ret = [None]*( len( x.split('$') ) )
    ret[1::2] = x.split('$')[1::2]
    ret[::2] = [ notex(n) for n in nomath ]
    return ' $ ' + ''.join(ret) + ' $ '

# ----------------------------------------------------------------------

def now():
    """Timestamp to label output, formatted YYYYMMDD_hhmmss."""
    return ( znt(lt().tm_year, 4) + znt(lt().tm_mon, 2) +
             znt(lt().tm_mday, 2) + '_' + znt(lt().tm_hour, 2) +
             znt(lt().tm_min, 2) + znt(lt().tm_sec, 2) )

# ----------------------------------------------------------------------

def znt(x, width=0):
    """Pads an integer with zeros. Floats are truncated."""
    return str( int(x) ).zfill(width)
