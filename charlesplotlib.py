# Charles McEachern

# Spring 2016

# Note: This document wraps at column 72. 

# ######################################################################
# ############################################################# Synopsis
# ######################################################################

# The plot window object is a wrapper around Matplotlib, designed to
# create plots which look nice in a dissertation or talk. 

# ######################################################################
# ################################################## Import Dependencies
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

# ######################################################################
# ##################################################### Helper Functions
# ######################################################################

# Grab a sebset of a dictionary by keys.
def dslice(d, keys):
  return dict( (key, val) for key, val in d.items() if key in keys )

# Combine several dictionaries, whether listed as arguments or as the
# entries in a list or generator. 
def dsum(*args):
  dlist = list( args[0] ) if len(args)==1 else args
  return dict( sum( [ list( d.items() ) for d in dlist ], [] ) )




def values(*args):
    if len(args) == 0:
        return None
    elif len(args) == 1:
        return [ x for x in list( args[0] ) if x is not None ]
    else:
        return [ x for x in  args if x is not None ]






# Safely get the maximum of a possibly-empty list or iterator. As in
# Python2, None counts as lower than any number.
def nax(*args):
    return np.max( np.array( values(*args) ) )

# Safely get the minimum of a possibly-empty list or iterator. 
def nin(*args):
    return np.min( np.array( values(*args) ) )



# Format a chunk of text to be non-math LaTeX. 
def notex(x):
  if '\n' in x:
    return ' $ \n $ '.join( notex(y) for y in x.split('\n') )
  else:
    return '\\operatorname{' + x.replace(' ', '\\;') + '}'

# Timestamp to label output, formatted yyyymmdd_hhmmss. 
def now():
  return ( znt(lt().tm_year, 4) + znt(lt().tm_mon, 2) +
           znt(lt().tm_mday, 2) + '_' + znt(lt().tm_hour, 2) +
           znt(lt().tm_min, 2) + znt(lt().tm_sec, 2) )

# Take a string and split math and non-math on dollar signs. 
def tex(x):
  nomath = x.split('$')[::2]
  ret = [None]*( len( x.split('$') ) )
  ret[1::2] = x.split('$')[1::2]
  ret[::2] = [ notex(n) for n in nomath ]
  return ' $ ' + ''.join(ret) + ' $ '

# Pads an integer with zeros. Floats are truncated. 
def znt(x, width=0):
  return str( int(x) ).zfill(width)

# ######################################################################
# ########################################################### Color Maps
# ######################################################################

# There are two color maps. One goes from white to black, through
# blues and reds. The other is diverging, with white in the middle and
# dark cool/warm colors at the low/high extremes. 
def _cmap_(ncolors=1024, diverging=False):
  if diverging:
    u = np.linspace(0., 1., 1024)
    bot = cubehelix.cmap(start=0.5, rot=-0.5)(u)
    top = cubehelix.cmap(start=0.5, rot=0.5, reverse=True)(u)
    ch = lsc.from_list( 'ch_div', np.vstack( (bot, top) ) )
    return ListedColormap( ch( np.linspace(0.05, 0.95, ncolors) ) )
  else:
    ch = cubehelix.cmap(start=1.5, rot=-1, reverse=True)
    return ListedColormap( ch( np.linspace(0., 1., ncolors) ) )

# ######################################################################
# #################################################### Global Parameters
# ######################################################################

_ncolors_ = 7

# For talks, all font sizes will be scaled up. 
_fontscale_ = 1.
_fontsize_ = 10

# Format for image output: PDF, PNG, SVG, etc. 
_savefmt_ = 'pdf'

# If we save any plots, it will be to a timestamped directory. 
_savepath_ = os.environ['HOME'] + '/Desktop/plots/' + now()

# #####################################################################
# ######################################################### Axis Params
# #####################################################################

class axparams(dict):

  def __init__(self, xlims, ylims, zlims, cax):
    global _ncolors_

    print(xlims)
    print(ylims)
    print(zlims)



    xparams = self.foo('x', *xlims)

    yparams = self.foo('y', *ylims)

    zmin, zmax = zlims

    # If the z values are all positive, to within a tolerance, we use
    # the sequential colormap. 
    if zmin > 0 or np.abs(zmin) < 0.01*np.abs(zmax):
      levels = np.linspace(0, zmax, _ncolors_ + 1 )
      cmap = _cmap_( _ncolors_ )
    # Otherwise, we use the diverging colormap. 
    else:
      zabs = np.max( np.abs( (zmin, zmax) ) )
      levels = np.linspace(-zabs, zabs, _ncolors_ + 1 )
      cmap = _cmap_( _ncolors_, diverging=True )
    # Ticks go in the center of each color level. 
    zticks = 0.5*( levels[1:] + levels[:-1] )
    norm = BoundaryNorm(levels, cmap.N)
    ColorbarBase( cax, cmap=cmap, ticks=zticks, 
                  norm=norm, orientation='horizontal' )

    cax.set_xticklabels( [ self.fmt(t) for t in zticks ] )

    zparams = {'cmap':cmap, 'levels':levels, 'norm':norm}

    return dict.__init__( self, dsum(xparams, yparams, zparams) )

  def foo(self, name, imin, imax):

    ticks = np.linspace(imin, imax, 5)

    ticklabels = [ self.fmt(t) for t in ticks ]

    lims = (imin, imax)

    return { name + 'ticks':ticks,
             name + 'ticklabels':ticklabels,
             name + 'lims':lims }

  def fmt(self, z):
    return '$' + str( int(z) ) + '$'
    
# #####################################################################
# ######################################################### Plot Window
# #####################################################################

class plotwindow:

  # Array of Plot Cells. 
  cells = None

  # Footer axis, right axis, and title axis. 
  fax, rax, tax = None, None, None

  # Arrays of header axes and left axes (to label rows and columns). 
  haxes, laxes = None, None

  # Keep track of the default font size. 
  fontsize = None

  # -------------------------------------------------------------------
  # -------------------------------------------- Initialize Plot Window
  # -------------------------------------------------------------------

  def __init__(self, nrows=1, ncols=1, slope=0.8, _cells_=None, landscape=False):
    global _fontscale_, _fontsize_

    # TODO: All we should be doing at this point is creating an array
    # of cells. Figuring out how many cells to plot, the proportions of
    # the plot, etc, should happen as late as possible (so that those
    # parameters can be adjusted). 

    # Sometimes, temporary plot windows are created, allowing
    # manipulation of a slice of the cells array. 
    if _cells_ is not None:
      self.cells = _cells_
      return
    # The width of the plot matches the width of text area. For a
    # paper, that's taken to be 5.75" (which is the text width in the
    # LaTeX dissertation template). For a talk, it's taken to be 10".
    inchwidth = 10. if landscape else 5.75
    # For a wider window, use a larger font size. 
    _fontsize_ = ( 15 if landscape else 10 )*_fontscale_
    # Set the text to use LaTeX. 
    rc( 'font', **{ 'family':'sans-serif', 'sans-serif':['Helvetica'], 
                    'size':str( _fontsize_ ) } )
    rc('text', usetex=True)
    rc('text.latex', preamble='\\usepackage{amsmath}, ' +
                              '\\usepackage{amssymb}, ' + 
                              '\\usepackage{color}')
    # The window will be broken up into some number of equally-sized
    # tiles. That's the unit we use to specify the relative sizes of
    # plot elements. 
    titleheight = int( 20*_fontscale_ )
    headheight = int( 10*_fontscale_ if ncols > 1 else 1 )
    footheight = 10
    sidewidth = 10
    cellpad = 5
    labelpad = int( 20*_fontscale_ )
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

        print(top, bot, left, right)


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
    return plotwindow( _cells_=cells )

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

    print('imax:', nax( cell.imax(i) for cell in self.cells.flatten() ) )


    return nax( cell.imax(i) for cell in self.cells.flatten() )

  def imin(self, i):
    return nin( cell.imin(i) for cell in self.cells.flatten() )

  # -------------------------------------------------------------------
  # -------------------------------------------------- Style Parameters
  # -------------------------------------------------------------------

  def style(self, **kargs):
    global _fontsize_

    for key, val in kargs.items():

      targs = { 'x':0.5, 'y':0.5, 'horizontalalignment':'center', 
                'verticalalignment':'center'}

      if key=='clabs':
        targs['fontsize'] = str( int( _fontsize_ ) )
        [ h.text(s=tex(v), **targs) for v, h in zip(val, self.haxes) ]

      elif key=='rlabs':
        targs['fontsize'] = str( int( _fontsize_ ) )
        [ l.text(s=tex(v), **targs) for v, l in zip(val, self.laxes) ]

      elif key=='title':
        targs['fontsize'] = str( 1.2*_fontsize_ )
        self.tax.text(s=tex(val), **targs)

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

    print(axlims)


    kwargs = axparams(*axlims, cax=self.fax)
    [ cell.draw(**kwargs) for cell in self.cells.flatten() ]

    # Only the leftmost cells get y axis labels and tick labels. 
    self[:, 1:].style(yticklabels=(), ylabel='')
    # Only the bottom cells get x axis labela and tick labels. 
    self[:-1, :].style(xticklabels=(), xlabel='')

    # If the flag -i was given, save the output as an image.
    if '-i' in argv and isinstance(filename, str):
      # Make sure there's a directory to put the output in. 
      if not os.path.exists( _savepath_ ):
        os.makedirs( _savepath_ )
      # Save the image. If no format is specified, use the default. 
      if '.' in name:
        out = _savepath_ + '/' + filename
      else:
        out = _savepath_ + '/' + filename + '.' + _savefmt_
      print('Saving ' + out)
      return plt.savefig(out)
    # Otherwise, show the plot on the screen. 
    else:
      return plt.show()

# #####################################################################
# ########################################################### Plot Cell
# #####################################################################

class plotcell:

  bars = None
  contours = None
  lines = None
  meshes = None

  # -------------------------------------------------------------------
  # ---------------------------------------------- Initialize Plot Cell
  # -------------------------------------------------------------------

  def __init__(self, ax):
    self.ax = ax
    return

  # -------------------------------------------------------------------
  # ---------------------------------------------------------- Add Data
  # -------------------------------------------------------------------

  def bar(self, x, y, *args, **kargs):
    # Make sure we have a list to store these bar plots. 
    if self.bars is None:
      self.bars = []
    # Store the bar plot. We'll actually add it to the plot later. 
    self.bars.append( (x, y, args, kargs) )
    return

  def contour(self, x, y, z, *args, **kargs):
    # Make sure we have a list to store these contours. 
    if self.contours is None:
      self.contours = []
    # Store the contour. We'll actually add it to the plot later. 
    self.contours.append( (x, y, z, args, kargs) )
    return

  def line(self, x, y, *args, **kargs):
    # Make sure we have a list to store these contours. 
    if self.lines is None:
      self.lines = []
    # Store the line. We'll actually add it to the plot later. 
    self.lines.append( (x, y, args, kargs) )
    return

  def mesh(self, x, y, z, *args, **kargs):
    # Make sure we have a list to store these meshes. 
    if self.meshes is None:
      self.meshes = []
    # Store the mesh. We'll actually add it to the plot later. 
    self.meshes.append( (x, y, z, args, kargs) )
    return

  # -------------------------------------------------------------------
  # ------------------------------------------------- Find Cell Extrema
  # -------------------------------------------------------------------

  def imax(self, i):
    b, c, l, m = None, None, None, None
    if self.lines is not None:
      b = nax( (x, y, None)[i] for x, y, args, kargs in self.bars )
    if self.contours is not None:
      c = nax( (x, y, z)[i] for x, y, z, args, kargs in self.contours )
    if self.meshes is not None:
      m = nax( (x, y, z)[i] for x, y, z, args, kargs in self.meshes )
    if self.lines is not None:
      l = nax( (x, y, None)[i] for x, y, args, kargs in self.lines )
    return nax(b, c, l, m)

  def imin(self, i):
    b, c, l, m = None, None, None, None
    if self.lines is not None:
      b = nin( (x, y, None)[i] for x, y, args, kargs in self.bars )
    if self.contours is not None:
      c = nin( (x, y, z)[i] for x, y, z, args, kargs in self.contours )
    if self.meshes is not None:
      m = nin( (x, y, z)[i] for x, y, z, args, kargs in self.meshes )
    if self.lines is not None:
      l = nin( (x, y, None)[i] for x, y, args, kargs in self.lines )
    return nin(b, c, l, m)

  # -------------------------------------------------------------------
  # -------------------------------------------------- Style Parameters
  # -------------------------------------------------------------------

  def style(self, **kargs):

    for key, val in kargs.items():

      if key=='xlabel':
        self.ax.set_xlabel( tex(val) )

      elif key=='xlims':
        self.ax.set_xlim(val)

      elif key=='xticklabels':
        self.ax.set_xticklabels(val)

      elif key=='xticks':
        self.ax.set_xticks(val)

      elif key=='ylabel':
        self.ax.set_ylabel( tex(val) )

      elif key=='ylims':
        self.ax.set_ylim(val)

      elif key=='yticklabels':
        self.ax.set_yticklabels(val)

      elif key=='yticks':
        self.ax.set_yticks(val)

      else:
        print('WARNING -- unrecognized style parameter', key)

    return

  # -------------------------------------------------------------------
  # --------------------------------------------------------- Draw Data
  # -------------------------------------------------------------------

  def draw(self, **kwargs):

    # TODO: Handle limits, ticks, tick labels for x, y, and z. 

    ckeys, mkeys = ('cmap', 'levels'), ('cmap', 'norm')

    axkeys = ( 'xlims', 'xticks', 'xticklabels',
               'ylims', 'yticks', 'yticklabels' )

    self.style( **dslice(kwargs, axkeys) )

    # Handle contours first, if any. 
    if self.contours is not None:
      for x, y, z, args, kargs in self.contours:
        ckargs = dsum( kargs, dslice(kwargs, ckeys) )
        self.ax.contourf(x, y, z, *args, **ckargs)
    # Handle the color mesh, if any. 
    if self.meshes is not None:
      for x, y, z, args, kargs in self.meshes:
        mkargs = dsum( kargs, dslice(kwargs, mkeys) )
        self.ax.pcolormesh(x, y, z, *args, **mkargs)
    # Draw the bar plots, if any. 
    if self.bars is not None:
      for x, y, args, kargs in self.bars:
        self.ax.bar(x, y, *args, **kargs)
    # Draw the lines, if any. 
    if self.lines is not None:
      for x, y, args, kargs in self.lines:
        self.ax.plot(x, y, *args, **kargs)

    '''
    f, l = ('left', 'right') if not self.flipx else ('right', 'left')
    self.ax.xaxis.get_majorticklabels()[0].set_horizontalalignment(f)
    self.ax.xaxis.get_majorticklabels()[-1].set_horizontalalignment(l)
    self.ax.yaxis.get_majorticklabels()[0].set_verticalalignment('bottom')
    self.ax.yaxis.get_majorticklabels()[-1].set_verticalalignment('top')
    '''
    return































# #############################################################################
# ########################################################## Plot Window Object
# #############################################################################

# The Plot Window is a wrapper around PyPlot which handles the high-level
# commands -- subplot spacing, titles, labels, etc. It contains an array of
# Plot Cell objects, which keep track of the actual data. 

class plotWindow:

  # We keep a color axis for the color bar, a title axis, an array of header
  # axes for column labels, an array of side axes for row labels, a side header
  # axis to label the row labels, and a footer axis just in case. Data axes are
  # stored by the individual Plot Cells. Also a unit axis. 
  cax = None
  fax = None
  hax = None
  sax = None
  shax = None
  tax = None
  uax = None

  fax = None

  # The Plot Window also holds an array of Plot Cells, one for each data axis. 
  cells = None
  # Keep track of the style of color bar, if any, we'll be using. Use 'log' for
  # a log scale, 'sym' for a symmetric log scale, and 'lin' for a linear scale.
  # For no color bar, use False or None. 
  colorbar = None
  # Overwrite the default number of colors. 
  ncolors = 8
  # Overwrite the automatically-determined color bar range. 
  zmaxManual = None
  # Do we want to specify units for the color bar tick labels? 
  unit = ''


  fontfactor = 1.


  # ---------------------------------------------------------------------------
  # ---------------------------------------------------- Adjust Plot Parameters
  # ---------------------------------------------------------------------------

  def setParams(self, **kargs):
    # Keyword parameters used for centering text in axes. 
    targs = {'x':0.5, 'y':0.5, 'horizontalalignment':'center', 
             'verticalalignment':'center'}
    # Address the parameters one at a time. 
    for key, val in kargs.items():
      # Keys are caps insensitive. 
      key = key.lower()
      # Accept a list of strings as column labels. 
      if key=='collabels':
        for col, label in enumerate(val):
          self.hax[col].text(s='$' + label + '$', **targs)
      # Turn on the color bar, and specify its scale. 
      elif key=='colorbar':
        self.colorbar = val
        if self.colorbar:
          self.cax.axis('on')

      # Write something in the foot label. 
      elif key=='footer':
          self.fax.text(s='$' + val + '$', **targs)

      # Overwrite the default number of colors. 
      elif key=='ncolors':
        self.ncolors = val
      # Accept a list of strings as row labels. 
      elif key=='rowlabels':
        for row, label in enumerate(val):
          self.sax[row].text(s='$' + label + '$', **targs)
      # Sometimes, we may want to label the row labels. 
      elif key=='rowlabellabel':
        self.shax.text(s='$' + val + '$', **targs)
      # By default, axis limits are common to all plots. 
      elif key=='sharelimits':
        self.sharelimits = bool(val)
      # Put a sideways label in the color bar axis. 
      elif key=='sidelabel':
        targs['horizontalalignment'] = 'left'
        self.cax.text(s='$' + val + '$', rotation='vertical', **targs)
        targs['horizontalalignment'] = 'center'
      # Accept a string as the window supertitle. 
      elif key=='title':
        fontsize = ( 12 if not self.landscape else 24 )*self.fontfactor
        self.tax.text(s='$' + val + '$', fontsize=fontsize, **targs)
      # In case we want to put units on the color bar tick labels. 
      elif key=='unit':
        self.unit = val
      # Put a little label over the color bar indicating units. 
      elif key=='unitlabel':
        self.uax.text(s='$' + val + '$', **targs)
      # Overwrite the automatically-determined color bar range. 
      elif key=='zmax':
        self.zmaxManual = val
      # Any other parameters get sent to the cells. 
      else:
        [ cell.setParams( **{key:val} ) for cell in self.cells.flatten() ]
    return

  # ---------------------------------------------------------------------------
  # ---------------------------------------------------------- Get Cell Extrema
  # ---------------------------------------------------------------------------

  # We standardize color levels and axis ranges across all cells.

  def xmax(self):
    return max( cell.xmax() for cell in self.cells.flatten() )

  def ymax(self):
    return max( cell.ymax() for cell in self.cells.flatten() )

  def zmax(self):
    return max( cell.zmax() for cell in self.cells.flatten() )

  # Looking at minima is tricky, since some of them may be None, which is
  # smaller than any number. 

  def xmin(self):
    xmn = [ cell.xmin() for cell in self.cells.flatten() ]
    return None if max(xmn) is None else min( x for x in xmn if x is not None )

  def ymin(self):
    ymn = [ cell.ymin() for cell in self.cells.flatten() ]
    return None if max(ymn) is None else min( y for y in ymn if y is not None )

  def zmin(self):
    zmn = [ cell.zmin() for cell in self.cells.flatten() ]
    return None if max(zmn) is None else min( z for z in zmn if z is not None )

  # ---------------------------------------------------------------------------
  # ------------------------------------------------------------- Render Window
  # ---------------------------------------------------------------------------

  # Once all of the contours are loaded, we can standardize the plot domain and
  # color levels. 
  def render(self, filename=None):
    # Use the most extreme x and y values to set the plot domain. Snap to
    # integers, but don't round based on tiny bits of numerical noise. 
    xmin = None if self.xmin() is None else np.round( self.xmin() )
    xmax = None if self.xmax() is None else np.round( self.xmax() )
    ymin = None if self.ymin() is None else np.round( self.ymin() )
    ymax = None if self.ymax() is None else np.round( self.ymax() )

    if np.iscomplexobj(xmin):
      print('xmin is complex! ')
    if np.iscomplexobj(xmax):
      print('xmax is complex! ')
    if np.iscomplexobj(ymin):
      print('ymin is complex! ')
    if np.iscomplexobj(ymax):
      print('ymax is complex! ')

#    xmin = np.floor( float( format(self.xmin(), '.4e') ) )
#    xmax = np.ceil( float( format(self.xmax(), '.4e') ) )
#    ymin = np.floor( float( format(self.ymin(), '.4e') ) )
#    ymax = np.ceil( float( format(self.ymax(), '.4e') ) )
    self.setParams( xlims=(xmin, xmax), ylims=(ymin, ymax) )
    # Only the leftmost cells get y axis labels and tick labels. 
    for cell in self.cells[:, 1:].flatten():
      if not cell.rightaxis:
        cell.setParams( ylabel='', yticklabels=() )
    # Only the bottom cells get x axis labela and tick labels. 
    for cell in self.cells[:-1, :].flatten():
      cell.setParams( xlabel='', xticklabels=() )
    # Use the most extreme contour value among all plots to set the color bar. 
    kargs = {'cax':self.cax, 'colorbar':self.colorbar, 'ncolors':self.ncolors, 'unit':self.unit}
    if self.zmaxManual is not None:
      colors = plotColors(zmax=self.zmaxManual, **kargs)
    else:
      colors = plotColors(zmax=self.zmax(), **kargs)
    # Send the color params to each cell. 
    [ cell.render(**colors) for cellRow in self.cells for cell in cellRow ]
    # If given a filename, save the image. 
    if filename is not None:
      # Make sure the folder exists. 
      if not os.path.exists( os.path.dirname(filename) ):
        os.makedirs( os.path.dirname(filename) )
      # Silently save the image. 
      plt.savefig(filename)
      return True
    # Otherwise, display it. 
    else:
      plt.show()
      return True

# #############################################################################
# ############################################################ Plot Cell Object
# #############################################################################

class plotCell:

  # If this cell contains a contour, we'll need to hold the spatial coordinates
  # and the data values. We also keep room for any arguments for contourf. 
  x, y, cz, mz, ckargs, mkargs = None, None, None, None, None, None
  # A plot can have any number of lines drawn on it. Those will be stored here. 
  lines = None

  bars = None


  # If we manually set the axis limits, we want to ignore the automatically-set
  # limits that come down the line later. 
  xlims, ylims = (None, None), (None, None)
  # If we're on a log scale, we need different rules for placing ticks. 
  xlog, ylog = False, False
  # Keep track if we're supposed to be tracing the outline of our domain, such
  # as if the data is dipole-shaped. Or the whole grid. 
  grid, outline = False, False
  # Cells can be small. Let's try to keep the number of ticks under control.
  nxticks, nyticks = 3, 4
  # Sometimes we want an extra axis label on the right. Make sure the window
  # doesn't delete it when it's cleaning up the non-edge ticks and labels. 
  rightaxis = False

  xtickrelax, ytickrelax = False, False

  flipx, flipy = False, False


  # ---------------------------------------------------------------------------
  # ----------------------------------------------------------- Initialize Cell
  # ---------------------------------------------------------------------------

  def __init__(self, ax):
    self.ax = ax
    return

  # ---------------------------------------------------------------------------
  # ------------------------------------------------------- Set Cell Parameters
  # ---------------------------------------------------------------------------

  def setParams(self, **kargs):
    # Scroll through the parameters one at a time. 
    for key, val in kargs.items():
      # Keys are caps insensitive. 
      key = key.lower()
      # Sometimes we want to sneak in an extra axis of labels. 
      if key=='axright' and bool(val) is True:
        self.rightaxis = True
        self.ax.yaxis.set_label_position('right')
        self.ax.yaxis.tick_right()
        self.ax.yaxis.set_ticks_position('both')
      # Draw Earth. 
      elif key=='earth':
        q = {'l':90, 'r':270, 't':0, 'b':180}[ val[0] ]
        self.ax.add_artist( Wedge( (0, 0), 1, q,       q + 180, fc='w') )
        self.ax.add_artist( Wedge( (0, 0), 1, q + 180, q + 360, fc='k') )
      # Flip an axis. 
      elif key=='flipx' and bool(val):
        self.flipx = True

      # Put some text in the corner. 
      elif key=='lcorner':
        targs = {'x':0.03, 'y':0.03, 'horizontalalignment':'left', 
                 'verticalalignment':'bottom', 'transform':self.ax.transAxes,
                 'fontsize':10}
        self.ax.text(s='$' + val + '$', **targs)

      # Put some text in the corner. 
      elif key=='rcorner':
        targs = {'x':0.97, 'y':0.03, 'horizontalalignment':'right', 
                 'verticalalignment':'bottom', 'transform':self.ax.transAxes,
                 'fontsize':10}
        self.ax.text(s='$' + val + '$', **targs)

      # Draw the grid. 
      elif key=='grid':
        self.grid = val
      # Sometimes we have to finagle with the number of ticks. 
      elif key=='nxticks':
        self.nxticks = val
      elif key=='nyticks':
        self.nyticks = val
      # Draw an outline around the plot contents. 
      elif key=='outline':
        self.outline = val
      # Add text inside the cell, along the top. If we want to do anything more
      # sophisticated with text, like control its position or rotation or
      # color or size, we'll probably need to add a setText method. 
      elif key=='text':
        targs = {'x':0.5, 'y':0.5, 'horizontalalignment':'center', 
                 'verticalalignment':'center', 'transform':self.ax.transAxes}
        self.ax.text(s='$' + val + '$', **targs)

      elif key=='toptext':
        targs = {'x':0.5, 'y':0.90, 'horizontalalignment':'center', 
                 'verticalalignment':'top', 'transform':self.ax.transAxes}
        self.ax.text(s='$' + val + '$', **targs)

      # Horizontal axis coordinate. 
      elif key=='x':
        self.x = val
      # Label the horizontal axis. 
      elif key=='xlabel':
        self.ax.set_xlabel('' if not val else '$' + val + '$')
      # Change padding between axis and label. 
      elif key=='xlabelpad':
        self.ax.xaxis.labelpad = val
      # Set horizontal axis domain. 
      elif key.startswith('xlim'):
        # If the limits are set manually, we want to ignore the automatic
        # limits that come down the line later. 
        self.xlims = ( val[0] if self.xlims[0] is None else self.xlims[0], 
                       val[1] if self.xlims[1] is None else self.xlims[1] )
      # Set log horizontal scale. 
      elif key=='xlog' and val is True:
        self.ax.set_xscale('log')
        self.xlog = True
      # Set the horizontal axis tick labels manually. 
      elif key=='xticklabels':
        self.ax.set_xticklabels(val)
        self.nxticks = None

      elif key=='xtickrelax':
        self.xtickrelax = val

      # Set the horizontal axis ticks manually. 
      elif key=='xticks':
        self.ax.set_xticks(val)
        self.nxticks = None
      # Vertical axis coordinate. 
      elif key=='y':
        self.y = val
      # Label the vertical axis. 
      elif key=='ylabel':
        self.ax.set_ylabel('' if not val else '$' + val + '$')
      # Change padding between axis and label. 
      elif key=='ylabelpad':
        self.ax.yaxis.labelpad = val
      # Set the vertical axis domain. 
      elif key.startswith('ylim'):
        # If the limits are set manually, we want to ignore the automatic
        # limits that come down the line later. 
        self.ylims = ( val[0] if self.ylims[0] is None else self.ylims[0], 
                       val[1] if self.ylims[1] is None else self.ylims[1] )
      # Set log vertical scale. 
      elif key=='ylog' and val is True:
        self.ax.set_yscale('log')
        self.ylog = True
      # Set the vertical axis tick labels manually. 
      elif key=='yticklabels':
        self.ax.set_yticklabels(val)
        self.nyticks = None

      elif key=='ytickrelax':
        self.ytickrelax = val

      # Set the vertical axis ticks manually. 
      elif key=='yticks':
        self.ax.set_yticks(val)
        self.nyticks = None
      # Report any unfamiliar parameters. 
      else:
        print('WARNING: Unknown param', key, '=', val)
    return

  # ---------------------------------------------------------------------------
  # ------------------------------------------------------- Report Cell Extrema
  # ---------------------------------------------------------------------------

  # Cells all share a color bar (for contour plots) and axis limits (for line
  # plots). To manage that, the Plot Window asks each cell for its extrema. 

  def xmax(self):
    return None if self.x is None else np.max(self.x)

  def ymax(self):
    amax = None if self.y is None else np.max(self.y)
    bmax = None if self.bars is None else max( max( args[1] ) for args, kargs in self.bars )
    lmax = None if self.lines is None else max( max( args[1] ) for args, kargs in self.lines )
    return max(amax, bmax, lmax)

  def zmax(self):
    cmax = None if self.cz is None else np.max(self.cz)
    mmax = None if self.mz is None else np.max(self.mz)
    return max(cmax, mmax)

  # Minima are tricky, since None counts as smaller than any number. 

  def xmin(self):
    return None if self.x is None else np.min(self.x)

  def ymin(self):
    amin = None if self.y is None else np.min(self.y)
    bmin = None if self.bars is None else min( min( args[1] ) for args, kargs in self.bars )
    lmin = None if self.lines is None else min( min( args[1] ) for args, kargs in self.lines )
    nums = [ m for m in (amin, bmin, lmin) if m is not None ]
    return None if len(nums)==0 else min(nums)

  def zmin(self):
    cmin = None if self.cz is None else np.min(self.cz)
    mmin = None if self.mz is None else np.min(self.mz)
    nums = [ m for m in (cmin, mmin) if m is not None ]
    return None if len(nums)==0 else min(nums)

  # ---------------------------------------------------------------------------
  # ---------------------------------------------------------- Render Plot Cell
  # ---------------------------------------------------------------------------

  def render(self, **colors):
    # If this cell has a contour, lay that down first. 
    if self.cz is not None:
      # Use the color params we were passed, but allow keyword arguments from
      # the contour call to overwrite them. 
      citems = [ ( key, colors[key] ) for key in ('ticks', 'levels', 'norm', 'cmap') ]
      kargs = dict( citems + list( self.ckargs.items() ) )
      self.ax.contourf(self.x, self.y, self.cz, **kargs)
    # Same for a mesh. 
    if self.mz is not None:
      citems = [ ( 'norm', colors['mnorm'] if 'mnorm' in colors else None ), 
                 ( 'cmap', colors['mcmap'] if 'mcmap' in colors else None ) ]
      kargs = dict( citems + list( self.mkargs.items() ) )
      self.ax.pcolormesh(self.x, self.y, self.mz, **kargs)

    # Draw the bars. 
    if self.bars is not None:
      [ self.ax.bar(*args, **kargs) for args, kargs in self.bars ]

    # Optionally, draw the outline of the data. 
    if self.outline and self.x is not None and self.y is not None:
      [ self.ax.plot(self.x[i, :], self.y[i, :], 'k') for i in (0, -1) ]
      [ self.ax.plot(self.x[:, k], self.y[:, k], 'k') for k in (0, -1) ]
    # Or the whole grid. 
    if self.grid and self.x is not None and self.y is not None:
      x, y = self.x, self.y
      [ self.setLine(x[i, :], y[i, :], 'k') for i in range( x.shape[0] ) ]
      [ self.setLine(x[:, j], y[:, j], 'k') for j in range( x.shape[1] ) ]

    # Draw any lines. 
    if self.lines is not None:
      [ self.ax.plot(*args, **kargs) for args, kargs in self.lines ]
    # Set axis limits. 
    self.ax.set_xlim( self.xlims if not self.flipx else self.xlims[::-1] )
    self.ax.set_ylim(self.ylims)

    # There can be a lot of cells. Try to be economical. 
    if not self.xlog:
      if self.nxticks is not None:
        self.ax.xaxis.set_major_locator( plt.MaxNLocator(self.nxticks,
                                                         integer=True) )
      if not self.xtickrelax:
        f, l = ('left', 'right') if not self.flipx else ('right', 'left')
        self.ax.xaxis.get_majorticklabels()[0].set_horizontalalignment(f)
        self.ax.xaxis.get_majorticklabels()[-1].set_horizontalalignment(l)

    if not self.ylog:
      if self.nyticks is not None:
        self.ax.yaxis.set_major_locator( plt.MaxNLocator(self.nyticks, 
                                                         integer=True) )

      if not self.ytickrelax:
        self.ax.yaxis.get_majorticklabels()[0].set_verticalalignment('bottom')
        self.ax.yaxis.get_majorticklabels()[-1].set_verticalalignment('top')
    return

# #############################################################################
# ######################################################### Plot Colors Handler
# #############################################################################

# This class figures out the color levels and ticks to be used by all of the
# contour plots. It draws the color bar, then serves as a keyword dictionary
# for the contourf calls. 

class plotColors(dict):

  # ---------------------------------------------------------------------------
  # --------------------------------------------------------- Initialize Colors
  # ---------------------------------------------------------------------------

  def __init__(self, zmax, cax, colorbar=None, ncolors=None, unit=''):
    # Some plots don't have contours. 
    if not zmax or not cax or not colorbar:
      return dict.__init__(self, {})
    # Store the data scale so that it can be hard-wired into our normalization
    # functions. 
    self.colorbar = colorbar
    self.ncolors = ncolors if ncolors is not None else 8
    self.nticks = self.ncolors - 1
    self.unit = unit
    # Assemble the keyword parameters in a temporary dictionary. We'll then use
    # the dictionary constructor to build this object based on it. 
    temp = {}
    # Determine location of contour color levels and color bar ticks. 
    if self.colorbar=='log':
      temp['ticks'], temp['levels'] = self.logTicksLevels(zmax)
      temp['norm'] = LogNorm()
    elif self.colorbar=='lg':
      temp['ticks'], temp['levels'] = self.lgTicksLevels(zmax)
      temp['norm'] = LogNorm()
    elif self.colorbar=='sym':
      temp['ticks'], temp['levels'] = self.symTicksLevels(zmax)
      temp['norm'] = Normalize()
    elif self.colorbar=='phase':
      temp['ticks'], temp['levels'] = self.phaseTicksLevels(zmax)
      temp['norm'] = Normalize()
    elif self.colorbar=='pos':
      temp['ticks'], temp['levels'] = self.posTicksLevels(zmax)
      temp['norm'] = Normalize()

    elif self.colorbar=='pct':
      temp['ticks'], temp['levels'] = self.pctTicksLevels(zmax)
      temp['norm'] = LogNorm()

    else:
      temp['ticks'], temp['levels'] = self.linTicksLevels(zmax)
      temp['norm'] = Normalize()

    # Rework the color map to match the normalization of our ticks and levels. 
    temp['cmap'] = self.getCmap()

    # Kludge something together so this works for colormesh as well as contour. 
    temp['mcmap'], temp['mnorm'] = self.getMesh( temp )

    # Draw the color bar. 
    self.setColorbar(cax, **temp)
    # Become a dictionary of color parameters to be used by the contour plots. 
    return dict.__init__(self, temp)

  # ---------------------------------------------------------------------------
  # ----------------------------------- Tick Locations and Contour Color Levels
  # ---------------------------------------------------------------------------

  def linTicksLevels(self, zmax):
    # We put zmax at the top of the top color level. Ticks go at the middle of
    # color levels, as they do with symlog plots. 
    self.zmax = zmax
    levels = np.linspace(-self.zmax, self.zmax, self.ncolors)
    ticks = 0.5*( levels[1:] + levels[:-1] )
    # Make sure that the middle tick is exactly zero. 
    ticks[ len(ticks)/2 ] = 0.
    return ticks, levels

  def phaseTicksLevels(self, zmax):
    # This setup probably isn't very useful. But it'll be a good place to start
    # if we ever want a linear-scale color bar that bottoms out at zero. It
    # also sets tick labels to be fractions of pi, which looks nice. 
    self.zmax = np.pi/2
    self.zmin = 0
    self.nticks = self.ncolors
    ticks = np.linspace(self.zmin, self.zmax, self.nticks)
    levels = np.linspace(self.zmin, self.zmax, self.ncolors)
    return ticks, levels

  # Seems to work? Don't lean too heavily... it was just thrown together. 
  def posTicksLevels(self, zmax):
    # Linear scale from 0 to zmax. Tick at every other level. Put zmax at the
    # center of the top bin, and 0 at the bottom edge of the bottom bin. 
    dz = zmax/(self.nticks - 0.5)
    self.zmax = zmax + dz/2
    levels = np.linspace(0, self.zmax, self.ncolors)
    ticks = 0.5*( levels[1:] + levels[:-1] )[::2]
    return ticks, levels

  def logTicksLevels(self, zmax):
    # Color levels are centered on ticks. The top tick is a power of ten. Each
    # subsequent tick is down by sqrt(10). 
    power = np.ceil(np.log10(zmax) - 0.25)
    # Each color spans a factor of root ten. This is in contrast to the
    # symmetric log scale, where each color was a whole order of magnitude. The
    # goal is to, for each, have the same number of colors and the same number
    # of orders of magnitude. 
    # Symetric log scale with 7 colors will have three positive powers of ten,
    # three negative powers, and zero. The log scale will just have three
    # positive powers. Anything below there will automatically show 0, though
    # it won't be marked explicitly on the color bar. 
    self.zmax = 10.**(power + 0.25)
    self.zmin = self.zmax/10**(self.nticks/2 + 0.5)
    ticks = [ 10**(power - 0.5*i) for i in range(self.nticks) ]
    logMin, logMax = np.log10(self.zmin), np.log10(self.zmax)
    levels = np.logspace(logMin, logMax, self.ncolors)
    return ticks, levels




  def pctTicksLevels(self, zmax):
    # Hard-coded to have ticks at 10%, 1%, 0.1%. Several color levels between each tick. 
    halves = np.logspace(-2, 1, self.ncolors - 1)
    self.zmin = halves[0]*np.sqrt( halves[0]/halves[1] )
    self.zmax = halves[-1]*np.sqrt(halves[-1]/halves[-2] )
    levels = np.logspace(np.log10(self.zmin), np.log10(self.zmax), self.ncolors)
    ticks = np.array( (0.01, 0.1, 1, 10) )
    return ticks, levels





  def lgTicksLevels(self, zmax):
    # Same as log, but with base 2 instead of 10. 
    power = np.ceil(np.log2(zmax) - 0.25)
    self.zmax = 2.**(power + 0.25)
    self.zmin = self.zmax/2**(self.nticks/2 + 0.5)
    ticks = [ 2**(power - 0.5*i) for i in range(self.nticks) ]
    lgMin, lgMax = np.log2(self.zmin), np.log2(self.zmax)
    levels = np.logspace(lgMin, lgMax, self.ncolors, base=2)
    return ticks, levels

  def symTicksLevels(self, zmax):
    # Ticks are located at powers of ten. Color levels are centered on ticks. 
    power = np.ceil( np.log10( zmax/np.sqrt(10.) ) )
    self.zmax = np.sqrt(10.)*10**power
    # A tick at zero, then one per order of magnitude. 
    norders = (self.nticks - 1)/2
    pticks = [ 10**(power - i) for i in range(norders) ]
    plevels = [ np.sqrt(10.)*10**(power - i) for i in range(norders + 1) ]
    # For uniform tick spacing, the log cutoff is a factor of 10 below the
    # lowest positive tick. That is, it's where the next tick would be, if we
    # had one more tick. 
    self.zmin = min(pticks)/10.
    ticks = sorted( pticks + [0] + [ -tick for tick in pticks ] )
    levels = sorted( plevels + [ -level for level in plevels ] )
    return ticks, levels

  # ---------------------------------------------------------------------------
  # ----------------------------------------------- Data Interval Normalization
  # ---------------------------------------------------------------------------

  # Map from the unit interval to the data scale via linear scale. 
  def linNorm(self, x):
    return self.zmax*(2*x - 1)

  # Map from the data scale to the unit interval via linear scale. 
  def linMron(self, x):
    return 0.5 + 0.5*x/self.zmax

  # Map from the unit interval to the data scale via linear scale. 
  def phaseNorm(self, x):
    return x*self.zmax

  # Map from the data scale to the unit interval via linear scale. 
  def phaseMron(self, x):
    return x/self.zmax

  # Map from the unit interval to the data scale via log scale. 
  def logNorm(self, x):
    return self.zmin*(self.zmax/self.zmin)**x

  # Map from the log scaled data scale to the unit interval. 
  def logMron(self, x):
    return np.log10(x/self.zmin)/np.log10(self.zmax/self.zmin)

  # Map from the unit interval to the data scale via symmetric log scale. 
  def symNorm(self, x):
    if x>0.5:
      return self.zmin*(self.zmax/self.zmin)**(2*x - 1)
    elif x<0.5:
      return -self.zmin*(self.zmax/self.zmin)**(1 - 2*x)
    else:
      return 0

  # Map from the symmetric log scaled data scale to the unit interval. 
  def symMron(self, x):
    if x>self.zmin:
      return 0.5 + 0.5*np.log10(x/self.zmin)/np.log10(self.zmax/self.zmin)
    elif x<-self.zmin:
      return 0.5 - 0.5*np.log10(-x/self.zmin)/np.log10(self.zmax/self.zmin)
    else:
      return 0.5

  # ---------------------------------------------------------------------------
  # --------------------------------------------------- Mesh Norm and Color Map
  # ---------------------------------------------------------------------------

  # This is SUPER kludgey. Sorry. No time to make it pretty while writing! 
  def getMesh(self, temp):
    clevs = np.array( temp['levels'] )
    if self.colorbar in ('lg', 'log', 'pct'):
      ulevs = np.array( [ self.logMron(c) for c in clevs ] )
    elif self.colorbar=='pos':
      ulevs = ( clevs - clevs[0] )/( clevs[-1] - clevs[0] )
    elif self.colorbar=='lin':
      ulevs = np.array( [ self.linMron(c) for c in clevs ] )
    elif self.colorbar=='sym':
      ulevs = np.array( [ self.symMron(c) for c in clevs ] )
    else:
      print('WARNING: mesh can\'t handle that. ')
    clist = [ temp['cmap'](u) for u in 0.5*( ulevs[1:] + ulevs[:-1] ) ]
    cmap = ListedColormap(clist)
    norm = BoundaryNorm(clevs, cmap.N)
    return cmap, norm

  # ---------------------------------------------------------------------------
  # ------------------------------------------------------------- Set Color Bar
  # ---------------------------------------------------------------------------

  # Without SymLogNorm, we can't very well use the built-in color bar
  # functionality. Instead, we make our own: a tall, narrow contour plot. 
  def setColorbar(self, cax, **colorParams):
    # Unit interval axes. 
    X, Y = np.empty( (2, 1000) ), np.empty( (2, 1000) )
    for i in range(2):
      X[i, :] = i
      Y[i, :] = np.linspace(0, 1, 1000)
    # The contour values are just the Y axis, mapped to the data scale via
    # linear, log, or symmetric log normalizer. We'll also need the inverse
    # normalizers, since we have the tick values in the data scale, and we map
    # them to the Y axis (which is on the unit interval). And the formatters,
    # to make our ticks look pretty in LaTeX. 
    if self.colorbar=='log':
      # This is kludgey right now. Sorry. We can't use a real color bar for the
      # symmetric norm plot, since since SymLogNorm isn't defined. But we can't
      # use a renormalized color map for the log plot due to sampling
      # constraints. This is the odd case out right now. 
      norm, mron, fmtr = self.logNorm, self.logMron, self.logFormatter
      ColorbarBase(cax, boundaries=colorParams['levels'],
                   ticks=colorParams['ticks'], norm=colorParams['norm'],
                   cmap=colorParams['cmap'])
      cax.set_yticklabels( [ fmtr(t) for t in colorParams['ticks'] ] )
      return

    elif self.colorbar=='lg':
      norm, mron, fmtr = self.logNorm, self.logMron, self.lgFormatter
      ColorbarBase(cax, boundaries=colorParams['levels'],
                   ticks=colorParams['ticks'], norm=colorParams['norm'],
                   cmap=colorParams['cmap'])
      cax.set_yticklabels( [ fmtr(t) for t in colorParams['ticks'] ] )
      return

    elif self.colorbar=='pct':
      norm, mron, fmtr = self.logNorm, self.logMron, self.pctFormatter
      ColorbarBase(cax, boundaries=colorParams['levels'],
                   ticks=colorParams['ticks'], norm=colorParams['norm'],
                   cmap=colorParams['cmap'])
      cax.set_yticklabels( [ fmtr(t) for t in colorParams['ticks'] ] )
      return

    elif self.colorbar=='pos':
      fmtr = self.linFormatter
      ColorbarBase(cax, boundaries=colorParams['levels'],
                   ticks=colorParams['ticks'], norm=colorParams['norm'],
                   cmap=colorParams['cmap'])
      cax.set_yticklabels( [ fmtr(t).replace('+', '') for t in colorParams['ticks'] ] )
      return

    elif self.colorbar=='sym':
      norm, mron, fmtr = self.symNorm, self.symMron, self.symFormatter
    elif self.colorbar=='phase':
      norm, mron, fmtr = self.phaseNorm, self.phaseMron, self.phaseFormatter
    else:
      norm, mron, fmtr = self.linNorm, self.linMron, self.linFormatter
    # Draw the contour. 
    Z = np.vectorize(norm)(Y)
    cax.contourf( X, Y, Z, **colorParams)
    # Place the ticks appropriately on the unit interval (Y axis). 
    cax.set_yticks( [ mron(t) for t in colorParams['ticks'] ] )
    # Format tick names nicely. 
    cax.set_yticklabels( [ fmtr(t) for t in colorParams['ticks'] ] )
    # Put the color bar ticks on the right, get rid of the ticks on the bottom,
    # and hide the little notches in the color bar. 
    cax.yaxis.tick_right()
    cax.set_xticks( [] )
    cax.tick_params( width=0 )
    return

  # ---------------------------------------------------------------------------
  # ------------------------------------------------------ Tick Name Formatting
  # ---------------------------------------------------------------------------

  # We have to format the ticks for two reasons. First, because the color bar Y
  # axis is on the unit interval, not the data scale (and may not be normalized
  # properly). Second, because that's how we make sure to get dollar signs in
  # there so LaTeX handles the font rendering. 
  def linFormatter(self, x):
    # Zero is always zero. 
    if x==0:
      return '$0' + self.unit + '$'
    # If our numbers are around order unity, the top tick should show two
    # significant figures, and the rest should match that decimal place. 
    elif 1e-3<self.zmax<1e4:
      sign = '' if x<0 else '+'
      power = int( format(self.zmax, '.1e').split('e')[-1] )
      if power>1:
        xp = x/10.**power
        d0 = int(xp)
        d1 = int( round( 10*(xp - d0) ) )
        fx = format((d0 + 0.1*d1)*10**power, '.0f')
      else:
        digs = 1 - power
        fx = format(x, '.' + str(digs) + 'f')
      return '$' + sign + fx + self.unit + '$'
    else:
      # Cast the number in scientific notation. 
      s = format(x, '.1e').replace('e', ' \\cdot 10^{') + '}'
      # If the number is positive, throw a plus sign on there. 
      s = '+ ' + s if x>0 else s
      # Before returning, get rid of any extra digits in the exponent. 
      return '$' + s.replace('+0', '').replace('-0', '-') + self.unit + '$'

  def phaseFormatter(self, x):
    # Zero is always zero. 
    if x==0:
      return '$0' + self.unit + '$'
    else:
      # Fractions of pi. Don't put '1' in the numerator. 
      numer, denom = (x/np.pi).as_integer_ratio()
      if numer==1:
        return '${\\displaystyle \\frac{\\pi}{' + str(denom) + '}}' + self.unit + '$'
      else:
        return '${\\displaystyle \\frac{' + str(numer) + ' \\pi}{' + str(denom) + '}}' + self.unit + '$'

  def logFormatter(self, x):
    # Zero is always zero. 
    if x==0:
      return '$0$'
    # Half-power ticks don't get labels. 
    elif format(x, '.1e').startswith('3'):
      return ''
    # Otherwise, just keep the power of ten. 
    return '$ 10^{' + format(np.log10(x), '.0f') + '}' + self.unit + '$'

  def pctFormatter(self, x):
    if x == int(x):
      return '$' + str( int(x) ) + '\\%$'
    else:
      return '$' + str(x) + '\\%$'

  def lgFormatter(self, x):
    # Zero is always zero. 
    if x==0:
      return '$0$'
    # Half-power ticks don't get labels. 
    elif np.log2(x) != np.int( np.log2(x) ):
      return ''
    # Otherwise, just keep the power of ten. 
    return '$ 2^{' + format(np.log2(x), '.0f') + '}' + self.unit + '$'

  def symFormatter(self, x):
    # Zero is always zero. 
    if x==0:
      return '$0' + self.unit + '$'
    # Otherwise, just keep the sign and the power of ten. 
    power = format(np.log10( np.abs(x) ), '.0f')
    return '$ ' + ( '-' if x<0 else '+' ) + ' 10^{' + power + '}' + self.unit + '$'

# #############################################################################
# ############################################################ Helper Functions
# #############################################################################

# Turns a list of numbers (1, 2, 3) into the string '1x2x3'. 
def by(x):
  return str( x[0] ) + 'x' + by( x[1:] ) if len(x)>1 else str( x[0] )

# Convert a string to a complex or float. 
def com(x):
  if ',' not in x:
    return float(x)
  else:
    # Shave off the parentheses then split into real and imaginary parts. 
    re, im = x[1:-1].split(',')
    return (float(re) + float(im)*1j)

# Grab all files in the given directory. Remember that we always use absolute
# paths, and that directory names always end with a slash. 
def files(path=None, end=''):
  p = path if path is not None else os.getcwd()
  # Grab all files in the directory. 
  f = [ p + x for x in os.listdir(p) if os.path.isfile(p + x) ]
  # Only return the ones that end with our desired extension. 
  return sorted( x for x in f if x.endswith(end) )

# Given kargs full of lists, return a list of kargs (if we're making a series
# of images) or just one of them (if we're looking at the plot). 
def loopover(**kargs):
  lo = [ [] ]
  for key, vals in kargs.items():
    lo = [ l + [ (key, v) ] for l in lo for v in vals ]
  if '-i' not in argv:
    return [ dict( choice(lo) )  ]
  else:
    return [ dict(l) for l in lo ]

# Turn a string into a float or integer. 
def num(x):
  return int( float(x) ) if float(x)==int( float(x) ) else float(x)

# Two decimal places. If it's a number bigger than one, that's two sig figs. Less than one, only one sig fig, to save space. 
def tdp(x):

#  if not isinstance(x, np.float) or not isinstance(x, np.int) or not np.isfinite(x):
#    return '?'

  if x.size > 1 or not np.isfinite(x):
    return '?'

  if x == 0:
    return '0'
  elif x < 1:
    return str( float( format(x, '.0e') ) )
  elif x < 10:
    return str( float( format(x, '.1e') ) )
  else:
    return str( int( float( format(x, '.1e') ) ) )



# Make sure we don't throw anything infinite on the plot. 
def fmask(x):
  return masked_where(np.logical_not( np.isfinite(x) ), x)

# Also leave out any zeros. 
def zmask(x, thr=0):
  return masked_where(np.abs(x) <= thr, x)



