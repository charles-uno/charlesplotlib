# Charles McEachern

# Summer 2016

# ######################################################################
# ############################################################# Synopsis
# ######################################################################

# WIP...

# ######################################################################
# ############################################################## Imports
# ######################################################################

import numpy as np
from time import localtime as lt








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

def values(*args):
    """Take several arguments, or a single sequence or generator, and
    return a list of values. None-valued entries are trimmed out. 
    """
    if len(args) == 0:
        return []
    elif len(args) == 1:
        return [ x for x in list( args[0] ) if x is not None ]
    else:
        return [ x for x in  args if x is not None ]

# ----------------------------------------------------------------------

def nax(*args):
    """Get the maximum of a possibly-empty list or generator."""
    vals = values(*args)
    return np.max(vals) if vals else None

# ----------------------------------------------------------------------

def ned(*args):
    """Get the median of a possibly-empty list or generator."""
    vals = values(*args)
    return np.median(vals) if vals else None

# ----------------------------------------------------------------------

def nin(*args):
    """Get the minimum of a possibly-empty list or generator."""
    vals = values(*args)
    return np.min(vals) if vals else None

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




