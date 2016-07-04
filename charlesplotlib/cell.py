# Charles McEachern

# Summer 2016

# ######################################################################
# ############################################################# Synopsis
# ######################################################################

# WIP...

# ######################################################################
# ############################################################## Imports
# ######################################################################

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
    # Axis bounds. These are set by the plot window after all the data
    # is entered. Typically, all cells share the same bounds. 
    xmin, xmax, ymin, ymax = None, None, None, None
    # Axes can be log or linear. For the moment, at least, this is
    # specified by the user. It's hard to guess if an axis is supposed
    # to be log scaled! 
    xlog, ylog = False, False
    # Tick locations. These are set by the plot window -- after it asks
    # whether each axis is linear or log scaled.
    xticks, yticks = None, None
    # Tick labels are also set by the window. Only edge cells get them,
    # so that the grid can be packed a bit tighter. 
    xticklabels, yticklabels = None, None
    # Axis labels. These are set by the user -- usually at the window
    # level, which automatically passes them to only the edge cells.
    xlabel, ylabel = None, None
    # All cells share a common color bar. To that end, color information
    # is passed to each cell by the plot window (after it figures out
    # the appropriate scale, etc). 
    cmap, levels, norm = None, None, None

    # ==================================================================
    # =================================================== Initialization
    # ==================================================================

    def __init__(self, ax):
        """WIP..."""
        # For the moment, we take the axis object at initialization.
        # This can probably be pushed back to the draw() call, though,
        # now that calls are rearranged. 
        self.ax = ax
        # Fire up lists to keep track of the data to be shown on this
        # cell. Any combination of bars, contours, lines, and meshes can
        # coexist (although the user doesn't have control over the order
        # in which they are drawn). 
        self.bars, self.lines = [], []
        self.contours, self.meshes = [], []
        return

    # ==================================================================
    # ========================================================= Add Data
    # ==================================================================

    def bar(self, *args, **kwargs):
        """Store a bar plot, to plot later."""

        if len(args) < 2:
            raise ValueError('Bar plot must have at least two sequential arguments.')

        # Add a dummy z value to make later comparisons easy. 
        xyzargs = args[:2] + (None,) + args[:2]

        return self.bars.append( (xyzargs, kwargs) )

    # ------------------------------------------------------------------

    def contour(self, *args, **kwargs):
        """Store a contour plot, to plot later."""

        if len(args) < 3:
            raise ValueError('Contour plot must have at least three sequential arguments.')

        return self.contours.append( (args, kwargs) )

    # ------------------------------------------------------------------

    def line(self, *args, **kwargs):
        """Store a line plot, to plot later."""

        if len(args) < 2:
            raise ValueError('Line plot must have at least two sequential arguments.')
        # Add a dummy z value to make later comparisons easy. 
        xyzargs = args[:2] + (None,) + args[:2]

        return self.lines.append( (xyzargs, kwargs) )

    # ------------------------------------------------------------------

    def mesh(self, *args, **kwargs):
        """Store a mesh plot, to plot later."""

        if len(args) < 3:
            raise ValueError('Mesh plot must have at least three sequential arguments.')

        return self.meshes.append( (args, kwargs) )

    # ------------------------------------------------------------------

    def text(self, *args, **kwargs):
        """Store a text element, to add to the plot later."""
        self.texts.append( (args, kwargs) )

    # ==================================================================
    # ====================================================== Get Extrema
    # ==================================================================

    def imax(self, i):
        """Get the maximum in the given dimension of all bars, contours,
        lines, and meshes this plot holds.
        """
        bmax = helpers.nax( args[i] for args, kwargs in self.bars )
        cmax = helpers.nax( args[i] for args, kwargs in self.contours )
        lmax = helpers.nax( args[i] for args, kwargs in self.lines )
        mmax = helpers.nax( args[i] for args, kwargs in self.meshes )
        return helpers.nax(bmax, cmax, lmax, mmax)

    # ------------------------------------------------------------------

    def imin(self, i):
        """Get the minimum in the given dimension of all bars, contours,
        lines, and meshes this plot holds.
        """
        bmin = helpers.nin( args[i] for args, kwargs in self.bars )
        cmin = helpers.nin( args[i] for args, kwargs in self.contours )
        lmin = helpers.nin( args[i] for args, kwargs in self.lines )
        mmin = helpers.nin( args[i] for args, kwargs in self.meshes )
        return helpers.nin(bmin, cmin, lmin, mmin)

    # ==================================================================
    # ================================================= Style Parameters
    # ==================================================================

    def style(self, **kargs):

        for key, val in kargs.items():

#            print('applying', key, val)

            if key == 'cmap':
                self.cmap = val

            elif key == 'levels':
                self.levels = val

            elif key == 'norm':
                self.norm = val

            elif key=='xlabel':
                self.xlabel = helpers.tex(val)
#                self.ax.set_xlabel( helpers.tex(val) )

            elif key=='xlims':
                self.xmin, self.xmax = val
#                self.ax.set_xlim(val)

            elif key == 'xlog':
                self.xlog = bool(val)
#                if bool(val):
#                    self.ax.set_xscale('log')
#                    self.ax.minorticks_off()
#                else:
#                    self.ax.set_xscale('linear')

            elif key=='xticklabels':
                self.xticklabels = val
#                self.ax.set_xticklabels(val)

            elif key=='xticks':
                self.xticks = val
#                self.ax.set_xticks(val)

            elif key=='ylabel':
                self.ylabel = helpers.tex(val)
#                self.ax.set_ylabel( helpers.tex(val) )

            elif key=='ylims':
                self.ymin, self.ymax = val
#                self.ax.set_ylim(val)

            elif key == 'ylog':
                self.ylog = bool(val)
#                if bool(val):
#                    self.ax.set_yscale('log')
#                    self.ax.minorticks_off()
#                else:
#                    self.ax.set_yscale('linear')

            elif key=='yticklabels':
                self.yticklabels = val
#                self.ax.set_yticklabels(val)

            elif key=='yticks':
                self.yticks = val
#                self.ax.set_yticks(val)

            else:
                print('WARNING -- unrecognized style parameter', key)

        return

    # ==================================================================
    # ======================================================== Draw Cell
    # ==================================================================

    def draw(self):
        """Draw this cell."""

#        self.style(**kwargs)

#        ckeys, mkeys = ('cmap', 'levels'), ('cmap', 'norm')

#        axkeys = ( 'xlims', 'xticks', 'xticklabels',
#                   'ylims', 'yticks', 'yticklabels' )

#        self.style( **helpers.dslice(kwargs, axkeys) )


        # Adjust the axes. 
        if self.xlabel:
            self.ax.set_xlabel(self.xlabel)
        if self.ylabel:
            self.ax.set_ylabel(self.ylabel)

        self.ax.set_xlim( (self.xmin, self.xmax) )
        self.ax.set_ylim( (self.ymin, self.ymax) )

        if self.xlog:
            self.ax.set_xscale('log')
        if self.ylog:
            self.ax.set_yscale('log')
        self.ax.minorticks_off()

        self.ax.set_xticks(self.xticks)
        self.ax.set_yticks(self.yticks)

        if self.xticklabels:
            self.ax.set_xticklabels(self.xticklabels)
        else:
            self.ax.set_xticklabels( () )

        if self.yticklabels:
            self.ax.set_yticklabels(self.yticklabels)
        else:
            self.ax.set_yticklabels( () )

        # Handle contours first, if any. 
        for args, kwargs in self.contours:

            # We want the user-supplied keywords to trump those provided by the plot window (though hopefully they will not collide). 
            if 'cmap' not in kwargs:
                kwargs['cmap'] = self.cmap
            if 'levels' not in kwargs:
                kwargs['levels'] = self.levels

            self.ax.contourf(*args, **kwargs)

        # Handle the color mesh, if any. 
        for args, kwargs in self.meshes:

            # We want the user-supplied keywords to trump those provided by the plot window (though hopefully they will not collide). 
            if 'cmap' not in kwargs:
                kwargs['cmap'] = self.cmap
            if 'norm' not in kwargs:
                kwargs['norm'] = self.norm

            self.ax.pcolormesh(*args, **kwargs)

        # Draw the bar plots, if any. 
        for args, kwargs in self.bars:
            # Get rid of the dummy argument we added in bar(). 
            xyargs = args[:2] + args[3:]
            self.ax.bar(*xyargs, **kwargs)

        # Draw the lines, if any. 
        for args, kwargs in self.lines:
            # Get rid of the dummy argument we added in line(). 
            xyargs = args[:2] + args[3:]
            self.ax.plot(*xyargs, **kwargs)



        '''
        f, l = ('left', 'right') if not self.flipx else ('right', 'left')
        self.ax.xaxis.get_majorticklabels()[0].set_horizontalalignment(f)
        self.ax.xaxis.get_majorticklabels()[-1].set_horizontalalignment(l)
        self.ax.yaxis.get_majorticklabels()[0].set_verticalalignment('bottom')
        self.ax.yaxis.get_majorticklabels()[-1].set_verticalalignment('top')
        '''
        return




# ######################################################################

class cell(object):

    bars, contours, lines, meshes = None, None, None, None

    xlabel = None
    xmin, xmax = None, None
    xticks, xticklabels = None, None
    xlog = None

    ylabel = None
    ymin, ymax = None, None
    yticks, yticklabels = None, None
    ylog = None

    cmap = None
    levels = None
    norm = None

    # ==================================================================

    def __init__(self, ax):
        self.ax = ax
        self.bars = []
        self.contours = []
        self.lines = []
        self.meshes = []
        return

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

    def imin(self, i):
        """Get the minimum in the given dimension of all bars, contours,
        lines, and meshes this plot holds.
        """
        bmin = helpers.nin( (x, y, None)[i] for x, y, a, k in self.bars )
        cmin = helpers.nin( (x, y, z)[i] for x, y, z, a, k in self.contours )
        lmin = helpers.nin( (x, y, None)[i] for x, y, a, k in self.lines )
        mmin = helpers.nin( (x, y, z)[i] for x, y, z, a, k in self.meshes )
        return helpers.nin(bmin, cmin, lmin, mmin)







