
import datetime as dt
import matplotlib
#matplotlib.use('Agg')
from matplotlib.colors import BoundaryNorm
from matplotlib.colorbar import ColorbarBase
import matplotlib.patheffects as PathEffects
import matplotlib.pylab as plt
from matplotlib import patches
import numpy as np
import sys

from . import helpers

# LaTeX fonts.

matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = 'Roboto Condensed'
matplotlib.rcParams['text.latex.preamble'] = [
#    r'\usepackage{cmbright}',
    r'\usepackage[sfdefault,condensed]{roboto}',
#    r'\usepackage{venturis}',
    r'\usepackage{sansmath}',
    r'\sansmath'
]

#matplotlib.rcParams['font.family'] = 'sans-serif'
#matplotlib.rcParams['font.size'] = '14'

# ######################################################################

_labels = False

# ######################################################################

class Plot(object):

    title = None

    xticks, yticks, zticks = None, None, None
    xlabel, ylabel, zlabel = None, None, None

    xticklabels, yticklabels = None, None

    xlims, ylims, zlims = None, None, None

    ncolors = 13

    nticks = 5

    clabels, rlabels = None, None

    _colorbar = True

    # ------------------------------------------------------------------

    def __init__(self, rows=1, cols=1):
        self.cmap = helpers.seq_cmap()
        self._rows, self._cols = rows, cols
        self.subplots = np.empty( [rows, cols], dtype=object )
        for i in range(rows):
            for j in range(cols):
                self.subplots[i, j] = Subplot()
        return


    # ------------------------------------------------------------------
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.subplots.flatten()[key]
        else:
            return self.subplots[key]

    # ------------------------------------------------------------------

    def getnorm(self):
        if not any( x.meshes for x in self.subplots.flatten() ):
            self._colorbar = False
            return None
        self._colorbar = True
        z0, z1 = self.zticks[0], self.zticks[-1]
        dz = (z1 - z0)/(self.ncolors - 1.)
        zlevels = np.linspace(z0 - dz/2, z1 + dz/2, self.ncolors + 1)
        return BoundaryNorm(zlevels, self.cmap.N)

    # ------------------------------------------------------------------

    def draw(self, filename=None):
        global _labels
        norm = self.getnorm()
        # If we have labels, make room for a color bar.
        if not self._colorbar:
            self._colorbar = _labels
        axdict = getaxes(rows=self._rows, cols=self._cols, colorbar=self._colorbar)
        self.__dict__.update(axdict)
        if norm:
            ColorbarBase(
                self.bax,
                cmap=self.cmap,
                ticks=self.zticks,
                norm=norm,
                orientation='horizontal',
            )
            self.bax.xaxis.tick_top()
            if self.zticklabels:
                self.bax.set_xticklabels(self.zticklabels)
        kwargs = dict(
                x=0.5,
                y=0.5,
                horizontalalignment='center',
                verticalalignment='center',
        )
        if self.xticks:
            xlims = min(self.xticks), max(self.xticks)
            [ x.set_xticks(self.xticks) for x in self.dax.flatten() ]
            [ x.set_xlim(xlims) for x in self.dax.flatten() ]
        if self.title:
            self.tax.text(s=self.title, fontsize=24, **kwargs)
        if self.xlabel:
            self.xax.text(s=self.xlabel, fontsize=18, **kwargs)
        if self.ylabel:
            self.yax.text(s=self.ylabel, fontsize=18, rotation=90, **kwargs)
        if self.clabels:
            [ x.text(s=y, fontsize=16, **kwargs) for x, y in zip(self.cax, self.clabels) ]
        if self.rlabels:
            [ x.text(s=y, fontsize=16, **kwargs) for x, y in zip(self.rax, self.rlabels) ]
        if self.xlims:
            [ x.set_xlim(self.xlims) for x in self.dax.flatten() ]
        if self.xticks:
            [ x.set_xticks(self.xticks) for x in self.dax.flatten() ]
        if self.ylims:
            [ x.set_ylim(self.ylims) for x in self.dax.flatten() ]
        if self.yticks:
            [ x.set_yticks(self.yticks) for x in self.dax.flatten() ]
        if self.xticklabels:
            [ x.set_xticklabels(self.xticklabels) for x in self.dax[-1, :] ]
        if self.yticklabels:
            [ x.set_yticklabels(self.yticklabels) for x in self.dax[:, 0] ]
        handles, labels = [], []
        for sp, ax in zip( self.subplots.flatten(), self.dax.flatten() ):
            kwargs = {'cmap':self.cmap, 'norm':norm, 'ax':ax}
            sp.draw(**kwargs)
            for handle, label in zip( *ax.get_legend_handles_labels() ):
                if label not in labels:
                    handles.append(handle), labels.append(label)
        if _labels:
#            for color, label in _labels.items():
            plt.legend(
                handles,
                labels,
                numpoints=1,
                ncol=4,
                bbox_to_anchor=self.bax.get_position(),
                mode='expand',
                bbox_transform=plt.gcf().transFigure,
                borderaxespad=0,
                frameon=False,
                handletextpad=-0.1,
            )
        if '--save' in sys.argv and filename is not None:
            plotspath = '/home/charles/Desktop/plots/'
            timestamp = dt.datetime.now().strftime('%Y%m%d%H%M%S')
            filepath = plotspath + timestamp + '_' + filename
            print('Saving', filepath, '...')
            return plt.savefig(filepath)
        else:
            return plt.show()

# ======================================================================

def getaxes(rows=1, cols=1, colorbar=None):
    # Figure out how much space we need for the subplots.
    wcell, hcell, pad, bigpad = 100, 100, 5, 12
    htitle = 20
    wcells = cols*(wcell + pad) - pad
    hcells = rows*(hcell + pad) - pad

    # Make room for the color bar or legend, if necessary.
    if colorbar:
        hbar, barpad = bigpad, bigpad
    else:
        hbar, barpad = 0, 0

    # Sizes for the axis labels.
    hlabel, wlabel = pad, pad

    # If we have multiple columns, we'll want column labels.
    if cols > 1:
        hclab, clabpad = hlabel, pad
    else:
        hclab, clabpad = 0, 0

    # If we have multiple rows, we'll want row labels.
    if rows > 1:
        wrlab, rlabpad = bigpad, bigpad
    else:
        wrlab, rlabpad = 0, 0

    hgrid = barpad + hbar + pad + htitle + pad + hclab + clabpad + hcells + bigpad + hlabel + pad
    wgrid = pad + wlabel + bigpad + wcells + rlabpad + wrlab + pad

    # White background. Size is (width, height). Scale the window so the tiles proportion true.
    hfig, wfig = 8, 8*wgrid/hgrid

    plt.figure(figsize=(wfig, hfig), facecolor='w')
    # Tiles are (height, width).
    tiles = matplotlib.gridspec.GridSpec(hgrid, wgrid)
    plt.subplots_adjust(bottom=0., left=0., right=1., top=1.)

    axdict = {}

    # At the top is the colorbar/label axis.
    top = barpad
    bot = top + hbar
    left = pad + wlabel + bigpad
    right = -(pad + wrlab + rlabpad)
    bax = plt.subplot( tiles[top:bot, left:right] )
    bax.set_xticks( [] ), bax.set_yticks( [] )
    axdict['bax'] = bax

    # Right below that is the title axis.
    top = pad + hbar + barpad
    bot = top + htitle
    left = pad + wlabel + bigpad
    right = -(pad + wrlab + rlabpad)
    tax = plt.subplot( tiles[top:bot, left:right] )
    tax.axis('off')
    axdict['tax'] = tax

    # Under that are the column labels.
    top = pad + hbar + barpad + htitle + pad
    bot = top + hlabel
    cax = np.empty( [cols], dtype=object )
    for i in range(cols):
        left = pad + wlabel + bigpad + i*(wcell + pad)
        right = left + wcell
        cax[i] = plt.subplot( tiles[top:bot, left:right] )
    [ x.axis('off') for x in cax ]
    axdict['cax'] = cax

    # On the left we have an axis for the vertical label.
    top = pad + hbar + barpad + htitle + pad + hclab + clabpad
    bot = top + hcells
    left, right = pad, pad + wlabel
    yax = plt.subplot( tiles[top:bot, left:right] )
    yax.axis('off')
    axdict['yax'] = yax

    # To the right of the data we have row labels.
    rax = np.empty( [rows], dtype=object )
    right = -bigpad
    left = right - wrlab
    for j in range(rows):
        top = pad + hbar + barpad + htitle + pad + hclab + clabpad + j*(hcell + pad)
        bot = top + hcell
        rax[j] = plt.subplot( tiles[top:bot, left:right] )
    [ x.axis('off') for x in rax ]
    axdict['rax'] = rax

    # In the middle, we have the actual data axes themselves.
    dax = np.empty( [rows, cols], dtype=object )
    for i in range(rows):
        top = pad + hbar + barpad + htitle + pad + hclab + clabpad + i*(hcell + pad)
        bot = top + hcell
        for j in range(cols):
            left = pad + wlabel + bigpad + j*(wcell + pad)
            right = left + wcell
            dax[i, j] = plt.subplot( tiles[top:bot, left:right] )
    [ x.set_xticklabels( [] ) for x in dax[:-1, :].flatten() ]
    [ x.set_yticklabels( [] ) for x in dax[:, 1:].flatten() ]
    axdict['dax'] = dax

    # Finally, under the data, we have an axis for the horizontal label.
    bot = -pad
    top = bot - hlabel
    left = pad + wlabel + bigpad
    right = left + wcells
    xax = plt.subplot( tiles[top:bot, left:right] )
    xax.axis('off')
    axdict['xax'] = xax

    return axdict

# ######################################################################

class Subplot(object):

    # ------------------------------------------------------------------

    def __init__(self):
        self.meshes, self.lines, self.texts = [], [], []
        return

    # ------------------------------------------------------------------

    def mesh(self, *args, **kwargs):
        return self.meshes.append( (args, kwargs) )

    # ------------------------------------------------------------------

    def line(self, *args, **kwargs):
        global _labels
        if 'label' in kwargs:
            _labels = True
        return self.lines.append( (args, kwargs) )

    # ------------------------------------------------------------------

    def text(self, text, shadow=False, **kwargs):
        _kwargs = {
            'horizontalalignment':'center',
            'verticalalignment':'center',
        }

        if 'x' not in kwargs or 'y' not in kwargs:
            _kwargs['x'], _kwargs['y'] = 0.5, 0.5
            _kwargs.update(transform=self.dax.transAxes)

        if shadow:
            _kwargs.update(
                path_effects=[ PathEffects.withStroke(linewidth=10, foreground=shadow) ]
            )

        _kwargs.update(kwargs)
        _kwargs['s'] = text
        return self.texts.append( ( [], _kwargs ) )

    # ------------------------------------------------------------------

    def dots(self, *args, **kwargs):
        if 'color' in kwargs:
            kwargs['markeredgecolor'] = kwargs['color']
        if 'marker' not in kwargs:
            kwargs['marker'] = 'o'
        kwargs['linestyle'] = 'None'
        if 'size' in kwargs:
            kwargs['markersize'] = kwargs.pop('size')
        return self.line(*args, **kwargs)

    # ------------------------------------------------------------------

    def draw(self, **kwargs):
        for a, k in self.meshes:
            kwargs['ax'].pcolormesh(
                *a,
                cmap=kwargs['cmap'],
                norm=kwargs['norm'],
            )
        [ kwargs['ax'].plot(*a, **k) for a, k in self.lines ]
        [ kwargs['ax'].text(*a, **k) for a, k in self.texts ]
        return
