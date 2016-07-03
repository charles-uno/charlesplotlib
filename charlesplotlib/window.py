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

_ncolors = 7

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

    # Array of Plot Cells. 
    cells = None

    # Footer axis, right axis, and title axis. 
    fax, rax, tax = None, None, None

    # Arrays of header axes and left axes (to label rows and columns). 
    haxes, laxes = None, None

    # Keep track of the default font size. 
    fontsize = None

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
        cellpad = 5
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
#    self.fax.axis('off')
        [ l.axis('off') for l in self.laxes ]
        [ h.axis('off') for h in self.haxes ]

        return

  # -------------------------------------------------------------------
  # ------------------------------------------------- Access Plot Cells
  # -------------------------------------------------------------------

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

  # -------------------------------------------------------------------
  # ---------------------------------------------------------- Add Data
  # -------------------------------------------------------------------

    # If given a contour to plot, forward it to each cell. 
    def contour(self, *args, **kargs):
        return [ c.contour(*args, **kargs) for c in self.cells.flatten() ]

    # If given a line to plot, forward to each cell. 
    def line(self, *args, **kargs):
        return [ c.line(*args, **kargs) for c in self.cells.flatten() ]

    # If given a mesh to plot, forward to each cell. 
    def mesh(self, *args, **kargs):
        return [ c.mesh(*args, **kargs) for c in self.cells.flatten() ]

    # If given a bar plot, forward to each cell. 
    def bar(self, *args, **kargs):
        return [ c.bar(*args, **kargs) for c in self.cells.flatten() ]

  # -------------------------------------------------------------------
  # ------------------------------------------------- Find Cell Extrema
  # -------------------------------------------------------------------

    def imax(self, i):
        return helpers.nax( cell.imax(i) for cell in self.cells.flatten() )

    def imed(self, i):
        return helpers.ned( cell.imed(i) for cell in self.cells.flatten() )


    def imin(self, i):
        return helpers.nin( cell.imin(i) for cell in self.cells.flatten() )

  # -------------------------------------------------------------------
  # -------------------------------------------------- Style Parameters
  # -------------------------------------------------------------------

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
        global _savefmt_, _savepath_

        axlims = [ ( self.imin(i), self.imax(i) ) for i in range(3) ]

        kwargs = axparams(*axlims, cax=self.fax)
        [ cell.draw(**kwargs) for cell in self.cells.flatten() ]

        # Only the leftmost cells get y axis labels and tick labels. 
        self[:, 1:].style(yticklabels=(), ylabel='')
        # Only the bottom cells get x axis labela and tick labels. 
        self[:-1, :].style(xticklabels=(), xlabel='')

        # If the flag -i was given, save the output as an image.
        if '-i' in argv and isinstance(filename, str):
            # Make sure there's a directory to put the output in. 
            if not os.path.exists(_savepath):
                os.makedirs(_savepath)
            # Save the image. If no format is specified, use the default. 
            if '.' in name:
              out = _savepath + '/' + filename
            else:
              out = _savepath + '/' + filename + '.' + _savefmt_
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
    global _ncolors_

    xparams = self.foo('x', *xlims)

    yparams = self.foo('y', *ylims)

    zmin, zmax = zlims

    # If the z values are all positive, to within a tolerance, we use
    # the sequential colormap. 
    if zmin > 0 or np.abs(zmin) < 0.01*np.abs(zmax):
      levels = np.linspace(0, zmax, _ncolors + 1 )
      cmap = seq_cmap(_ncolors)
    # Otherwise, we use the diverging colormap. 
    else:
      zabs = np.max( np.abs( (zmin, zmax) ) )
      levels = np.linspace(-zabs, zabs, _ncolors + 1)
      cmap = sym_cmap(_ncolors)
    # Ticks go in the center of each color level. 
    zticks = 0.5*( levels[1:] + levels[:-1] )
    norm = BoundaryNorm(levels, cmap.N)
    ColorbarBase( cax, cmap=cmap, ticks=zticks, 
                  norm=norm, orientation='horizontal' )

    cax.set_xticklabels( [ self.fmt(t) for t in zticks ] )

    zparams = {'cmap':cmap, 'levels':levels, 'norm':norm}

    return dict.__init__( self, helpers.dsum(xparams, yparams, zparams) )






  def foo(self, name, imin, imax):

    ticks = np.linspace(imin, imax, 5)

    ticklabels = [ self.fmt(t) for t in ticks ]

    lims = (imin, imax)

    return { name + 'ticks':ticks,
             name + 'ticklabels':ticklabels,
             name + 'lims':lims }

  def fmt(self, z):
    return '$' + str( int(z) ) + '$'







# ######################################################################
# ########################################################### Color Maps
# ######################################################################

def sym_cmap(ncolors=1024):
    """Create a symmetric (diverging) colormap using cubehelix."""
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





