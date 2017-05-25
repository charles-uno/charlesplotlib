
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import gridspec, rc
from matplotlib.colors import BoundaryNorm
from matplotlib.colorbar import ColorbarBase
import matplotlib.patheffects as PathEffects
from matplotlib import patches
import numpy as np
import sys

from . import helpers

# ######################################################################

class Figure(object):

    lines = None
    meshes = None

    xlims, ylims, zlims = None, None, None

    # ------------------------------------------------------------------

    def __init__(self, rows=1, cols=1):
        # LaTeX fonts.
        rc('font', family='sans-serif', size='14')
        rc('text', usetex=True)
        rc('text.latex', preamble='\\usepackage{amsmath},\\usepackage{amssymb},\\usepackage{color}')
        # White background. Size is (width, height).
        plt.figure(figsize=(8, 8), facecolor='w')
        # Keep track of everything that will go on the plot. It'll all
        # get drawn at the end.

        # Tiles are (height, width).

        tiles = gridspec.GridSpec(100, 100)
        plt.subplots_adjust(bottom=0., left=0., right=1., top=1.)

        # Title axis.
        self.tax = plt.subplot( tiles[9:14, 8:-8] )
        self.tax.axis('off')
        self.tax.set_xticks( [] )
        self.tax.set_yticks( [] )

        # Legend/label axis.
        self.lax = plt.subplot( tiles[1:7, 8:-8] )
        self.lax.set_xticks( [] )
        self.lax.set_yticks( [] )

        # Data axis.
        self.dax = plt.subplot( tiles[16:93, 8:-8] )

        self.lines = []
        self.meshes = []
        return

    # ------------------------------------------------------------------

    def xticks(self, ticks):
        self.dax.set_xticks(ticks)

    # ------------------------------------------------------------------

    def yticks(self, ticks):
        self.dax.set_yticks(ticks)

    # ------------------------------------------------------------------

    def xlims(self, lims):
        self.dax.set_xlim(lims)

    # ------------------------------------------------------------------

    def ylims(self, lims):
        self.dax.set_ylim(lims)

    def zlims(self, lims):
        self.zlims = lims

    # ------------------------------------------------------------------

    def xlabel(self, text, *args, **kwargs):
        return self.dax.set_xlabel(helpers.tex(text), *args, **kwargs)

    # ------------------------------------------------------------------

    def ylabel(self, text, *args, **kwargs):
        return self.dax.set_ylabel(helpers.tex(text), *args, **kwargs)

    # ------------------------------------------------------------------

    def mesh(self, *args, **kwargs):
        self.meshes.append( (args, kwargs) )

    # ------------------------------------------------------------------

    def line(self, *args, **kwargs):
        return self.lines.append( (args, kwargs) )

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

    def highlight(self, xlims, ylims, **kwargs):
        return self.dax.add_patch(
            patches.Rectangle(
                ( xlims[0], ylims[0] ),
                xlims[1] - xlims[0],
                ylims[1] - ylims[0],
                **kwargs
            )
        )

    # ------------------------------------------------------------------

    def draw_lines(self):
        print(len(self.lines), 'lines to draw')

        if not self.lines:
            return

        for args, kwargs in self.lines:
            self.dax.plot(*args, **kwargs)
        plt.legend(
            numpoints=1,
            ncol=5,
            bbox_to_anchor=self.lax.get_position(),
            mode='expand',
            bbox_transform=plt.gcf().transFigure,
            borderaxespad=0.3,
            frameon=False,
            handletextpad=-0.4,

        )
        return

    # ------------------------------------------------------------------

    def draw_meshes(self):
        print(len(self.meshes), 'meshes to draw')

        if not self.meshes:
            return

        cmap = helpers.seq_cmap()

        if self.zlims:
            zmin, zmax = self.zlims
        else:
            zmin, zmax = 0, 12

        ncolors = 25
        nticks = 5
        zlvlstep = (zmax - zmin)/(ncolors - 1.)
        zlvlmin = zmin - 0.5*zlvlstep
        zlvlmax = zmax + 0.5*zlvlstep
        zlevels = np.linspace(zlvlmin, zlvlmax, ncolors + 1)
        zticks = np.linspace(zmin, zmax, nticks)


        print('ZTICKS:', zticks)


        norm = BoundaryNorm(zlevels, cmap.N)

        ColorbarBase(
            self.lax,
            cmap=cmap,
            ticks=zticks,
            norm=norm,
            orientation='horizontal',
        )
        self.lax.xaxis.tick_top()

        self.lax.set_xticklabels( [ helpers.fmt_int(x) for x in zticks ] )

        for args, kwargs in self.meshes:
            self.dax.pcolormesh(
                *args,
                cmap=cmap,
                norm=norm,
#                levels=zlevels,
            )

        return

    # ------------------------------------------------------------------

    def text(self, text, datacoords=False, shadow=None, **kwargs):

        _kwargs = {
            'x':0.5,
            'y':0.5,
            'horizontalalignment':'center',
            'verticalalignment':'center',
#            'transform':self.dax.transAxes
#            fontsize=12,
        }

        if not datacoords:
            _kwargs.update(transform=self.dax.transAxes)

        if shadow:
            _kwargs.update(
                path_effects=[ PathEffects.withStroke(linewidth=10, foreground=shadow) ]
            )



        _kwargs.update(kwargs)
        return self.dax.text(s=helpers.tex(text), **_kwargs)

    # ------------------------------------------------------------------

    def title(self, text):
        return self.tax.text(
            s=helpers.tex(text),
            x=0.5,
            y=0.5,
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=24,
        )

    # ------------------------------------------------------------------

    def draw(self, filename=None):
        self.draw_lines()
        self.draw_meshes()
        if '--save' in sys.argv and filename is not None:
            plotspath = '/home/charles/Desktop/plots/'
            timestamp = dt.datetime.now().strftime('%Y%m%d%H%M%S')
            filepath = plotspath + timestamp + '_' + filename
            print('Saving', filepath, '...')
            return plt.savefig(filepath)
        else:
            return plt.show()
