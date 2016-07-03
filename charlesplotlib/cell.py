# Charles McEachern

# Summer 2016

# ######################################################################
# ############################################################# Synopsis
# ######################################################################

# WIP...

# ######################################################################
# ############################################################## Imports
# ######################################################################

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
import matplotlib.pyplot as plt
import numpy as np
from sys import argv
from time import localtime as lt
from numpy.ma import masked_where



from . import helpers


# ######################################################################
# ############################################################ Plot Cell
# ######################################################################

class plotcell(object):
    """Keep track of all the data to be shown by a single subplot."""
    # Keep lists of the data that's to be shown on this subplot.
    bars, contours, lines, meshes = None, None, None, None

    # ==================================================================
    # =================================================== Initialization
    # ==================================================================

    def __init__(self, ax):
        """WIP..."""
        self.ax = ax
        self.bars = []
        self.contours = []
        self.lines = []
        self.meshes = []
        return

    # ==================================================================
    # ========================================================= Add Data
    # ==================================================================

    def bar(self, x, y, *args, **kwargs):
        """Store a bar plot, to plot later."""
        return self.bars.append( (x, y, args, kwargs) )

    # ------------------------------------------------------------------

    def contour(self, x, y, z, *args, **kwargs):
        """Store a contour plot, to plot later."""
        return self.contours.append( (x, y, z, args, kwargs) )

    # ------------------------------------------------------------------

    def line(self, x, y, *args, **kwargs):
        """Store a line plot, to plot later."""
        return self.lines.append( (x, y, args, kwargs) )

    # ------------------------------------------------------------------

    def mesh(self, x, y, z, *args, **kwargs):
        """Store a mesh plot, to plot later."""
        return self.meshes.append( (x, y, z, args, kwargs) )

    # ==================================================================
    # ====================================================== Get Extrema
    # ==================================================================

    def imax(self, i):
        """Get the maximum in the given dimension of all bars, contours,
        lines, and meshes this plot holds.
        """
        bmax = helpers.nax( (x, y, None)[i] for x, y, a, k in self.bars )
        cmax = helpers.nax( (x, y, z)[i] for x, y, z, a, k in self.contours )
        lmax = helpers.nax( (x, y, None)[i] for x, y, a, k in self.lines )
        mmax = helpers.nax( (x, y, z)[i] for x, y, z, a, k in self.meshes )
        return helpers.nax(bmax, cmax, lmax, mmax)

    # ------------------------------------------------------------------

    def imed(self, i):
        """Get the median in the given dimension of all bars, contours,
        lines, and meshes this plot holds.
        """
        bmed = helpers.ned( (x, y, None)[i] for x, y, a, k in self.bars )
        cmed = helpers.ned( (x, y, z)[i] for x, y, z, a, k in self.contours )
        lmed = helpers.ned( (x, y, None)[i] for x, y, a, k in self.lines )
        mmed = helpers.ned( (x, y, z)[i] for x, y, z, a, k in self.meshes )
        return helpers.ned(bmed, cmed, lmed, mmed)

    # ------------------------------------------------------------------

    def imin(self, i):
        """Get the minimum in the given dimension of all bars, contours,
        lines, and meshes this plot holds.
        """
        bmin = helpers.nin( (x, y, None)[i] for x, y, a, k in self.bars )
        cmin = helpers.nin( (x, y, z)[i] for x, y, z, a, k in self.contours )
        lmin = helpers.nin( (x, y, None)[i] for x, y, a, k in self.lines )
        mmin = helpers.nin( (x, y, z)[i] for x, y, z, a, k in self.meshes )
        return helpers.nin(bmin, cmin, lmin, mmin)

    # ==================================================================
    # ================================================= Style Parameters
    # ==================================================================

    def style(self, **kargs):

        for key, val in kargs.items():

            if key=='xlabel':
                self.ax.set_xlabel( helpers.tex(val) )

            elif key=='xlims':
                self.ax.set_xlim(val)

            elif key=='xticklabels':
                self.ax.set_xticklabels(val)

            elif key=='xticks':
                self.ax.set_xticks(val)

            elif key=='ylabel':
                self.ax.set_ylabel( helpers.tex(val) )

            elif key=='ylims':
                self.ax.set_ylim(val)

            elif key=='yticklabels':
                self.ax.set_yticklabels(val)

            elif key=='yticks':
                self.ax.set_yticks(val)

            else:
                print('WARNING -- unrecognized style parameter', key)

        return

    # ==================================================================
    # ======================================================== Draw Cell
    # ==================================================================

    def draw(self, **kwargs):
        """Draw this cell. Accept color keywords, which describe the
        shared color scale.
        """

        # TODO: Handle limits, ticks, tick labels for x, y, and z. 

        ckeys, mkeys = ('cmap', 'levels'), ('cmap', 'norm')

        axkeys = ( 'xlims', 'xticks', 'xticklabels',
                   'ylims', 'yticks', 'yticklabels' )

        self.style( **helpers.dslice(kwargs, axkeys) )

        # Handle contours first, if any. 
        for x, y, z, a, k in self.contours:
            ckwargs = helpers.dsum( k, helpers.dslice(kwargs, ckeys) )
            self.ax.contourf(x, y, z, *a, **ckwargs)

        # Handle the color mesh, if any. 
        for x, y, z, a, k in self.meshes:
            mkwargs = helpers.dsum( k, helpers.dslice(kwargs, mkeys) )
            self.ax.pcolormesh(x, y, z, *a, **mkwargs)

        # Draw the bar plots, if any. 
        for x, y, a, k in self.bars:
            self.ax.bar(x, y, *a, **k)

        # Draw the lines, if any. 
        for x, y, a, k in self.lines:
            self.ax.plot(x, y, *a, **k)

        '''
        f, l = ('left', 'right') if not self.flipx else ('right', 'left')
        self.ax.xaxis.get_majorticklabels()[0].set_horizontalalignment(f)
        self.ax.xaxis.get_majorticklabels()[-1].set_horizontalalignment(l)
        self.ax.yaxis.get_majorticklabels()[0].set_verticalalignment('bottom')
        self.ax.yaxis.get_majorticklabels()[-1].set_verticalalignment('top')
        '''
        return

