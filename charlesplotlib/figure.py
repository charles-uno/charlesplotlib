from . import helpers

import matplotlib.pyplot as plt
from matplotlib import gridspec, rc
from matplotlib.colors import BoundaryNorm
from matplotlib.colorbar import ColorbarBase
import numpy as np

class Figure(object):

    lines = None
    meshes = None

    # ------------------------------------------------------------------

    def __init__(self):
        # LaTeX fonts.
        rc('font', family='sans-serif', size='12')
        rc('text', usetex=True)
        rc('text.latex', preamble='\\usepackage{amsmath},\\usepackage{amssymb},\\usepackage{color}')
        # White background. Size is (width, height).
        plt.figure(figsize=(8, 8), facecolor='w')
        # Keep track of everything that will go on the plot. It'll all
        # get drawn at the end.

        # Tiles are (height, width).

        tiles = gridspec.GridSpec(30, 30)
        plt.subplots_adjust(bottom=0., left=0., right=1., top=1.)

        # Title axis.
        self.tax = plt.subplot( tiles[4:6, 2:-2] )
        self.tax.axis('off')
        self.tax.set_xticks( [] )
        self.tax.set_yticks( [] )

        # Legend/label axis.
        self.lax = plt.subplot( tiles[1:3, 2:-2] )
        self.lax.set_xticks( [] )
        self.lax.set_yticks( [] )

        # Data axis.
        self.dax = plt.subplot( tiles[7:28, 2:-2] )

        self.lines = []
        self.meshes = []
        return

    # ------------------------------------------------------------------

    def xlabel(self, text, *args, **kwargs):
        return plt.xlabel(helpers.tex(text), *args, **kwargs)

    # ------------------------------------------------------------------

    def ylabel(self, text, *args, **kwargs):
        return plt.ylabel(helpers.tex(text), *args, **kwargs)

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

    def draw_lines(self):
        print(len(self.lines), 'lines to draw')

        if not self.lines:
            return

        for args, kwargs in self.lines:
            self.dax.plot(*args, **kwargs)
        plt.legend(
            numpoints=1,
            ncol=4,
            bbox_to_anchor=self.lax.get_position(),
            mode='expand',
            bbox_transform=plt.gcf().transFigure,
            borderaxespad=0,
            frameon=False,
            handletextpad=-0.1,
        )
        return

    def draw_meshes(self):
        print(len(self.meshes), 'meshes to draw')

        if not self.meshes:
            return

        cmap = helpers.seq_cmap()

        zmin, zmax = 0, 12
        ncolors = 13
        nticks = 5
        zlvlstep = (zmax - zmin)/(ncolors - 1.)
        zlvlmin = zmin - 0.5*zlvlstep
        zlvlmax = zmax + 0.5*zlvlstep
        zlevels = np.linspace(zlvlmin, zlvlmax, ncolors + 1)
        zticks = np.linspace(zmin, zmax, nticks)

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


#        fmt = helpers.fmt_pow if zlog else helpers.fmt_int
#        cax.set_xticklabels( [ fmt(t) for t in zticks ] )



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

    def draw(self):
        self.draw_lines()
        self.draw_meshes()
        return plt.show()
