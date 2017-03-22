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

from .cell import plotcell
from . import helpers

# ######################################################################
# #################################################### Global Parameters
# ######################################################################

# TODO -- Should probably be in the window object.

_ncolors = 13

# With 13 colors, we can have 7, 5, or 4 ticks.
_nticks = 7

# For talks, all font sizes will be scaled up.
_fontscale = 1.
_fontsize = 10

# Format for image output: PDF, PNG, SVG, etc.
_savefmt = 'pdf'

# If we save any plots, it will be to a timestamped directory.
_savepath = os.environ['HOME'] + '/Desktop/plots/' + helpers.now()


# ######################################################################
# ########################################################## Plot Window
# ######################################################################

class plotwindow:

    # Array of plot cells.
    cells = None

    # Footer axis, right axis, and title axis.
    fax, rax, tax = None, None, None

    # Arrays of header axes and left axes (to label rows and columns).
    haxes, laxes = None, None

    # Keep track of the default font size.
    fontsize = None

    # The intention is for all cells to share axes.

    xlog, ylog, zlog = False, False, False

    xmin, xmax = None, None
    ymin, ymax = None, None
    zmin, zmax = None, None


    # ==================================================================
    # =================================================== Initialization
    # ==================================================================

    def __init__( self, nrows=1, ncols=1, slope=0.8, _cells=None,
                  landscape=False):

        global _fontscale, _fontsize

        # TODO: All we should be doing at this point is creating an array
        # of cells. Figuring out how many cells to plot, the proportions of
        # the plot, etc, should happen as late as possible (so that those
        # parameters can be adjusted).

        # Sometimes, temporary plot windows are created, allowing
        # manipulation of a slice of the cells array.
        if _cells is not None:
            self.cells = _cells
            return

        # The width of the plot matches the width of text area. For a
        # paper, that's taken to be 5.75" (which is the text width in the
        # LaTeX dissertation template). For a talk, it's taken to be 10".
        inchwidth = 10. if landscape else 5.75
        # For a wider window, use a larger font size.
        _fontsize = ( 15 if landscape else 10 )*_fontscale
        # Set the text to use LaTeX.
        rc( 'font', **{ 'family':'sans-serif', 'sans-serif':['Helvetica'],
                        'size':str(_fontsize) } )
        rc('text', usetex=True)
        rc('text.latex', preamble='\\usepackage{amsmath}, ' +
                                  '\\usepackage{amssymb}, ' +
                                  '\\usepackage{color}')
        # The window will be broken up into some number of equally-sized
        # tiles. That's the unit we use to specify the relative sizes of
        # plot elements.
        titleheight = int(20*_fontscale)
        headheight = int( 10*_fontscale if ncols > 1 else 1 )
        footheight = 10
        sidewidth = 10
        cellpad = 10
        labelpad = int(20*_fontscale)
        cellwidth = (210//ncols) - cellpad
        cellheight = int( cellwidth*slope )
        # Figure out the total number of tiles we need.
        tilewidth = 210 - cellpad + 2*sidewidth + 4*labelpad
        tileheight = ( titleheight + headheight + nrows*cellheight +
                       (nrows-1)*cellpad + 2*labelpad + footheight )
        # Set the window size to ensure that the tiles are square.
        inchheight = tileheight*inchwidth//tilewidth
        # Create the window. Tell it that we want the subplot area to go
        # all the way to the edges, then break that area up into tiles.
        fig = plt.figure(figsize=(inchwidth, inchheight), facecolor='w')
        fig.canvas.set_window_title('CPL Plotter')
        tiles = gridspec.GridSpec(tileheight, tilewidth)
        plt.subplots_adjust(bottom=0., left=0., right=1., top=1.)
        # Create a lattice of axes and use them to initialize an array of
        # plot cell objects.
        self.cells = np.empty( (nrows, ncols), dtype=object)
        for row in range(nrows):
            top = titleheight + headheight + row*(cellheight + cellpad)
            bot = top + cellheight
            for col in range(ncols):
                left = 2*labelpad + sidewidth + col*(cellwidth + cellpad)
                right = left + cellwidth

                ax = plt.subplot( tiles[top:bot, left:right] )

                self.cells[row, col] = plotcell(ax)
        # Space out the title axis.
        left = 2*labelpad + sidewidth
        self.tax = plt.subplot( tiles[:titleheight, left:-left] )
        # Space out an array of axes on the left to hold row labels.
        self.laxes = np.empty( (nrows,), dtype=object)
        left, right = labelpad, labelpad + sidewidth
        for row in range(nrows):
            top = titleheight + headheight + row*(cellheight + cellpad)
            bot = top + cellheight
            self.laxes[row] = plt.subplot( tiles[top:bot, left:right] )
        # Space out an array of header axes to hold column labels.
        self.haxes = np.empty( (ncols,), dtype=object)
        top, bot = titleheight, titleheight + headheight
        for col in range(ncols):
            left = 2*labelpad + sidewidth + col*(cellwidth + cellpad)
            right = left + cellwidth
            self.haxes[col] = plt.subplot( tiles[top:bot, left:right] )
        # Axis on the right.
        top, bot = titleheight + headheight, -footheight - 2*labelpad
        left, right = -labelpad - sidewidth, -labelpad
        self.rax = plt.subplot( tiles[top:bot, left:right] )
        # Foot axis for the color bar or legend.
        top, bot = -labelpad - footheight, -labelpad
        left = 2*labelpad + sidewidth
        self.fax = plt.subplot( tiles[top:bot, left:-left] )

        # Hide the axes that we just use for placing text.
        self.tax.axis('off')
        self.rax.axis('off')
#        self.fax.axis('off')
        [ l.axis('off') for l in self.laxes ]
        [ h.axis('off') for h in self.haxes ]
        return

    # ==================================================================
    # ================================================ Access Plot Cells
    # ==================================================================

    # The plot window itself doesn't actually handle any data. Instead,
    # data is forwarded to cells or slices of cells using array notation.
    def __getitem__(self, i):
        # If we're asked for a single cell, return that cell. Access can
        # use a 2D index or a 1D index (in which case the array is
        # flattened).
        if isinstance(i, int):
            return self.cells.flatten()[i]
        elif isinstance(i, tuple) and all( isinstance(j, int) for j in i ):
            return self.cells[i]
        # Otherwise, presumably, we were asked for a slice. In that case,
        # return a temporary plot window object which contains only the
        # requested slice of cells. Again, 1D and 2D notation are OK.
        if isinstance(i, tuple):
            cells = self.cells[i]
        else:
            self.cells.flatten()[i]
        return plotwindow(_cells=cells)

    # ==================================================================
    # ========================================================= Add Data
    # ==================================================================

    # If given a bar plot, forward to each cell.
    def bar(self, *args, **kwargs):
        """Forward a bar plot to each cell."""
        return [ c.bar(*args, **kwargs) for c in self.cells.flatten() ]

    # ------------------------------------------------------------------

    def contour(self, *args, **kwargs):
        """Forward a contour to each cell."""
        return [ c.contour(*args, **kwargs) for c in self.cells.flatten() ]

    # ------------------------------------------------------------------

    def line(self, *args, **kwargs):
        """Forward a line to each cell."""
        return [ c.line(*args, **kwargs) for c in self.cells.flatten() ]

    # ------------------------------------------------------------------

    def mesh(self, *args, **kwargs):
        """Forward a mesh to each cell."""
        return [ c.mesh(*args, **kwargs) for c in self.cells.flatten() ]

    # ==================================================================
    # ===================================================== Find Extrema
    # ==================================================================

    def imax(self, i):
        """In the given dimension, find the maximum value among all data
        in all cells.
        """
        return helpers.nax( cell.imax(i) for cell in self.cells.flatten() )

    # ------------------------------------------------------------------

    def imin(self, i):
        """In the given dimension, find the minimum value among all data
        in all cells.
        """
        return helpers.nin( cell.imin(i) for cell in self.cells.flatten() )

    # ------------------------------------------------------------------

    def ilog(self, i):
        """For the moment, at least, don't ask the cells whether or not
        they are log-scaled. That information is handled at the window
        level.
        """
        return (self.xlog, self.ylog, self.zlog)[i]

    # ==================================================================
    # ========================================== Window-Level Parameters
    # ==================================================================

    def style(self, **kargs):
        global _fontsize_

        for key, val in kargs.items():

            targs = { 'x':0.5, 'y':0.5, 'horizontalalignment':'center',
                      'verticalalignment':'center'}

            if key=='clabs':
                targs['fontsize'] = str( int(_fontsize) )
                [ h.text(s=helpers.tex(v), **targs) for v, h in zip(val, self.haxes) ]

            elif key=='rlabs':
                targs['fontsize'] = str( int(_fontsize) )
                [ l.text(s=helpers.tex(v), **targs) for v, l in zip(val, self.laxes) ]

            elif key=='title':
                targs['fontsize'] = str(1.2*_fontsize)
                self.tax.text(s=helpers.tex(val), **targs)

            # If an x label is given to the whole window, only set it on the bottom cells.
            elif key in ('xlabel', 'xticklabels'):
                [ c.style( **{key:val} ) for c in self[-1, :] ]

            elif key in ('ylabel', 'yticklabels'):
                [ c.style( **{key:val} ) for c in self[:, 0] ]

            # For log scaling, note the information here before passing it along.
            elif key == 'xlog':
                self.xlog = bool(val)
                [ c.style( **{key:val} ) for c in self.cells.flatten() ]

            elif key == 'ylog':
                self.ylog = bool(val)
                [ c.style( **{key:val} ) for c in self.cells.flatten() ]

            elif key == 'zlog':
                self.zlog = bool(val)

            elif key=='xlims':
                self.xmin, self.xmax = val

            elif key=='ylims':
                self.ymin, self.ymax = val

            elif key=='zlims':
                self.zmin, self.zmax = val

            # Anything else gets forwarded to each cell.
            else:
                [ c.style( **{key:val} ) for c in self.cells.flatten() ]

        return

  # -------------------------------------------------------------------
  # ---------------------------------------------------- Nuke Old Plots
  # -------------------------------------------------------------------

    def clear(self):
        return plt.close('all')

  # -------------------------------------------------------------------
  # --------------------------------------------- Save or Show the Plot
  # -------------------------------------------------------------------

    def draw(self, filename=None):
        global _savefmt, _savepath

        # If the user has set these manually, stick with them.

        xmin = self.xmin if self.xmin is not None else self.imin(0)
        xmax = self.xmax if self.xmax is not None else self.imax(0)
        ymin = self.ymin if self.ymin is not None else self.imin(1)
        ymax = self.ymax if self.ymax is not None else self.imax(1)
        zmin = self.zmin if self.zmin is not None else self.imin(2)
        zmax = self.zmax if self.zmax is not None else self.imax(2)

        axlims = ( (xmin, xmax, self.xlog),
                   (ymin, ymax, self.ylog),
                   (zmin, zmax, self.zlog) )

        kwargs = axparams(*axlims, cax=self.fax)

        self.style(**kwargs)

#        print(kwargs)

#        # Only the leftmost cells get y axis labels and tick labels.
#        self[:, 1:].style(yticklabels=(), ylabel='')

#        # Only the bottom cells get x axis labela and tick labels.
#        self[:-1, :].style(xticklabels=(), xlabel='')

#        [ cell.draw(**kwargs) for cell in self.cells.flatten() ]
        [ cell.draw() for cell in self.cells.flatten() ]

        # If the flag -i was given, save the output as an image.
        if '-i' in argv and isinstance(filename, str):
            # Make sure there's a directory to put the output in.
            if not os.path.exists(_savepath):
                os.makedirs(_savepath)
            # Save the image. If no format is specified, use the default.
            if '.' in name:
              out = _savepath + '/' + filename
            else:
              out = _savepath + '/' + filename + '.' + _savefmt
            print('Saving ' + out)
            return plt.savefig(out)
        # Otherwise, show the plot on the screen.
        else:
            return plt.show()





# #####################################################################
# ######################################################### Axis Params
# #####################################################################

class axparams(dict):

    def __init__(self, xlims, ylims, zlims, cax):
        global _ncolors, _nticks


        print('xmin, xmax, xlog:', xlims)

        xparams = self.foo('x', *xlims)
        yparams = self.foo('y', *ylims)

        zmin, zmax, zlog = zlims


        if zmax is None or zmin is None:
            return dict.__init__( self, helpers.dsum( xparams, yparams, {} ) )

        # Check if the z values are all positive, to within a tolerance.

        # TODO -- Handle values very close to zero, or exactly zero!

        zpos = ( zmin > 0 ) or np.abs(zmin) < 1e-6*np.abs(zmax)
        # If the z values are all positive, we use a sequential
        # colormap. Otherwise, we use a diverging one.
        if zmin >= 0:
            cmap = helpers.seq_cmap(_ncolors)
        else:
            cmap = helpers.div_cmap(_ncolors)

        print('zmin:', zmin)
        print('zmax:', zmax)
        print('zlog:', zlog)

        # For positive linear color scales, space levels uniformly. If
        # the minimum is much less than the maximum, start at zero.
        if zmin >= 0 and not zlog:
            print('positive linear')
            # If the minimum is small compared to the maximum, start at
            # zero. Get rid of the small positive offset.
            if zmin < 0.1*zmax:
                zmin = 0
            # Based on the minimum, maximum, and number of colors,
            # figure out where the levels need to go.
            zlvlstep = (zmax - zmin)/(_ncolors - 1.)
            zlvlmin = zmin - 0.5*zlvlstep
            zlvlmax = zmax + 0.5*zlvlstep
            zlevels = np.linspace(zlvlmin, zlvlmax, _ncolors + 1)
            # Ticks are spaced linearly from the minimum to the maximum.
            # The first and last ticks are centered in color levels. The
            # rest hopefully are too, but that depends on the number of
            # ticks and the number of colors.
            zticks = np.linspace(zmin, zmax, _nticks)
        # For positive log scales, ticks go at powers of ten.
        elif zmin > 0 and zlog:
            print('positive log')
            # Round up from the maximum and down from the minimum to the
            # next powers of ten.
            zmaxpow = int( np.ceil( np.log10(zmax) ) )
            zminpow = int( np.floor( np.log10(zmin) ) )
            # The above powers are centered in the first and last
            # levels. From that, and the number of colors, figure out
            # where the rest of the levels go.
            zlvlpowstep = (zmaxpow - zminpow)/(_ncolors - 1.)
            zlvlpowmin = zminpow - 0.5*zlvlpowstep
            zlvlpowmax = zmaxpow + 0.5*zlvlpowstep
            zlvlpow = np.linspace(zlvlpowmin, zlvlpowmax, _ncolors + 1)
            zlevels = 10**zlvlpow
            # Ticks are centered in the levels -- on a log scale.
            ztickpow = np.arange(zminpow, zmaxpow + 1)
            zticks = 10**ztickpow
        # For a symmetric linear scale, the positive and negative
        # extrema match to ensure that zero goes in the middle.
        elif zmin < 0 and not zlog:
            print('symmetric linear')
            # Find the maximum absolute value.
            zabs = np.max( np.abs( (zmin, zmax) ) )
            # As above, the min and max are centered in the first and
            # last levels. Assuming there are an odd number of colors,
            # the middle level will be white.
            zlvlstep = 2*zabs/(_ncolors - 1.)
            zlvlmin = -zabs - 0.5*zlvlstep
            zlvlmax =  zabs + 0.5*zlvlstep
            zlevels = np.linspace(zlvlmin, zlvlmax, _ncolors + 1)
            # Assuming an odd number of ticks, the middle one will be
            # zero.
            zticks = np.linspace(-zabs, zabs, _nticks)
        # If asked for a log scale but given negative values, bail. We
        # don't need symmetric log plots.
        else:
            raise NotImplementedError('Log scale with zmin < 0.')
        # From the determined ticks and levels, draw a colorbar.
        norm = BoundaryNorm(zlevels, cmap.N)
        ColorbarBase( cax, cmap=cmap, ticks=zticks,
                      norm=norm, orientation='horizontal' )
        # Tick labels can be formatted in a few ways.
        fmt = helpers.fmt_pow if zlog else helpers.fmt_int
        cax.set_xticklabels( [ fmt(t) for t in zticks ] )
        # Return a dictionary of color params to be distributed to each
        # cell. This is how they all know what color scale to observe.
        zparams = {'cmap':cmap, 'levels':zlevels, 'norm':norm}
        return dict.__init__( self, helpers.dsum(xparams, yparams, zparams) )




    def foo(self, name, imin, imax, ilog):


        if ilog and imin <=0:
            raise RuntimeError('Nonpositive minimum with log scale on ' + name + ' axis.')

        if ilog:
            pmin = int( np.floor( np.log10(imin) ) )
            pmax = int( np.ceil( np.log10(imax) ) )
            pticks = np.arange(pmin, pmax + 1)
            lims = (10**pmin, 10**pmax)
            ticks = 10**pticks
            ticklabels = [ helpers.fmt_pow(t) for t in ticks ]
        else:
            lims = ( int( np.floor(imin) ), int( np.ceil(imax) ) )


            print(name + 'min, max:', lims)

            ticks = sorted( np.linspace(lims[0], lims[1], 5) )

            ticklabels = [ helpers.fmt_int(t) for t in ticks ]

            print(name + 'ticks:', ticks)
            print(name + 'ticklabels:', ticklabels)



        return { name + 'ticks':ticks,
                 name + 'ticklabels':ticklabels,
                 name + 'lims':lims,
                 name + 'log':ilog }








def axis_params(imin, imax, ilog):
    """Given the minimum and maximum values along an axis, and if it's
    supposed to be log scaled, figure out ticks, etc.
    """
    global _ncolors, _nticks
    # Everything gets packed into a dictionary to be returned.
    axparams = {}

    # If the maximum is smaller than the minimum, the axis is meant to
    # be backwards. Keep track of that.
    if imax < imin:
        iflip = True
    imin, imax = min(imin, imax), max(imin, imax)
    # If there are negative values for a log axis, bail.
    if ilog and imin < 0:
        raise ValueError('Log axis can\'t have negative values!')
    # If everything is positive, use a sequential colormap. Otherwise,
    # use a diverging one.
    if imin >= 0:
        axparams['cmap'] = helpers.seq_cmap(_ncolors)
    else:
        axparams['cmap'] = helpers.div_cmap(_ncolors)
    # We figure out color levels for every axis. These values are
    # ignored for the x and y axes. Start with a linear positive axis.
    if not ilog and min(imin, imax) >= 0:
        # If the minimum is small, just start from zero.
        if np.abs(imin) < 0.1*np.abs(imax):
            imin = 0
        # The first tick is at the minimum. The last is at the maximum.
        ticks = np.linspace(imin, imax, _nticks)
        # Levels need to be a bit broader so that the ticks are centered
        # in each color.



        # TODO -- The x and y axes want a different number of ticks from the z axis!



'''



        if ilog:
            pmin = int( np.floor( np.log10(imin) ) )
            pmax = int( np.ceil( np.log10(imax) ) )
            pticks = np.arange(pmin, pmax + 1)
            lims = (10**pmin, 10**pmax)
            ticks = 10**pticks
            ticklabels = [ helpers.fmt_pow(t) for t in ticks ]

'''
