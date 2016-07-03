

import cubehelix
import matplotlib
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

import numpy as np
from . import helpers




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


