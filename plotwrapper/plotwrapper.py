
import datetime as dt
import matplotlib
import matplotlib.pylab as plt
import numpy as np
import sys

matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams["figure.titlesize"] = 14
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = 'Roboto Condensed'
matplotlib.rcParams['text.latex.preamble'] = [
    r'\usepackage[sfdefault,condensed]{roboto}',
    r'\usepackage{sansmath}',
    r'\sansmath'
]

# ======================================================================

class Plot(object):

    # ------------------------------------------------------------------

    def __init__(self, rows=1, cols=1, **kwargs):
        figsize=(cols*5, rows*5)

        self.fig, axes = plt.subplots(rows, cols, figsize=figsize)


        self.subplots = np.empty( [rows, cols], dtype=object )
        for row in range(rows):
            for col in range(cols):
                # Numpy shortcuts a 1xN array to 1D.
                if rows == 1:
                    self.subplots[row, col] = Subplot( axes[col] )
                else:
                    self.subplots[row, col] = Subplot( axes[row, col] )
        # We will often want to pass commands along to all subplots.
        # Let's make it convenient.
        self._subplots = self.subplots.flatten()
        return

    # ------------------------------------------------------------------

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.subplots.flatten()[key]
        else:
            return self.subplots[key]

    # ------------------------------------------------------------------

    def __getattr__(self, name):
        return getattr(plt, name)

    # ------------------------------------------------------------------

    def xlims(self, *args, **kwargs):
        return [ x.set_xlim(*args, **kwargs) for x in self._subplots ]

    def xlabel(self, *args, **kwargs):
        for subplot in self.subplots[-1, :]:
            subplot.set_xlabel(*args, **kwargs)
        return

    def xticks(self, *args, **kwargs):
        return [ x.set_xticks(*args, **kwargs) for x in self._subplots ]

    def xticklabels(self, *args, **kwargs):
        for subplot in self.subplots[:-1, :].flatten():
            subplot.set_xticklabels( [] )
        if 'rotation' not in kwargs:
            kwargs['rotation'] = 90
        for subplot in self.subplots[-1, :]:
            subplot.set_xticklabels(*args, **kwargs)
        return

    # ------------------------------------------------------------------

    def ylims(self, *args, **kwargs):
        return [ x.set_ylim(*args, **kwargs) for x in self._subplots ]

    def ylabel(self, *args, **kwargs):
        for subplot in self.subplots[:, 0]:
            subplot.set_ylabel(*args, **kwargs)
        return

    def yticks(self, *args, **kwargs):
        return [ x.set_yticks(*args, **kwargs) for x in self._subplots ]

    def yticklabels(self, *args, **kwargs):
        [ x.set_yticklabels( [] ) for x in self.subplots[:, 0:].flatten() ]
        return [ x.set_yticklabels(*args, **kwargs) for x in self.subplots[:, 0] ]

    # ------------------------------------------------------------------

    def title(self, *args, **kwargs):
        return plt.suptitle(*args, **kwargs)

    def collabels(self, *args, **kwargs):
        for subplot, label in zip(self.subplots[0, :], args):
            subplot.set_title(label, **kwargs)
        return



    # ------------------------------------------------------------------

    def draw(self, filename=None):

        plt.tight_layout()

        # Tight layout doesn't take the super title into account, so
        # let's squish everything down a bit to make room for that.
        self.fig.subplots_adjust(top=0.85)

        if '--save' in sys.argv and filename is not None:
            plotspath = '/home/charles/Desktop/plots/'
            timestamp = dt.datetime.now().strftime('%Y%m%d%H%M%S')
            filepath = plotspath + timestamp + '_' + filename
            print('Saving', filepath, '...')
            return plt.savefig(filepath)
        else:
            return plt.show()









# ======================================================================

class Subplot(object):

    # ------------------------------------------------------------------

    def __init__(self, ax):
        self.ax = ax
        return


    def line(self, *args, **kwargs):
        return self.ax.plot(*args, **kwargs)






    # ------------------------------------------------------------------

    def __getattr__(self, name):
        return getattr(self.ax, name)
