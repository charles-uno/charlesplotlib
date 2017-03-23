from . import helpers

import matplotlib.pyplot as plt
from matplotlib import rc


class Figure(object):

    lines = None

    def __init__(self):
        # LaTeX fonts.
        rc('font', family='sans-serif', size='12')
        rc('text', usetex=True)
        rc('text.latex', preamble='\\usepackage{amsmath},\\usepackage{amssymb},\\usepackage{color}')
        # White background.
        plt.figure(facecolor='w')
        # Keep track of everything that will go on the plot. It'll all
        # get drawn at the end.
        self.lines = []
        return

    def xlabel(self, text, *args, **kwargs):
        return plt.xlabel(helpers.tex(text), *args, **kwargs)

    def ylabel(self, text, *args, **kwargs):
        return plt.ylabel(helpers.tex(text), *args, **kwargs)

    def line(self, *args, **kwargs):
        return self.lines.append( (args, kwargs) )

    def mark(self, *args, **kwargs):
        args = ( (args[0],), (args[1],),) + args[2:]
        if 'color' in kwargs:
            kwargs['markeredgecolor'] = kwargs['color']
        if 'marker' not in kwargs:
            kwargs['marker'] = 'o'
        kwargs['linestyle'] = 'None'
        if 'size' in kwargs:
            kwargs['markersize'] = kwargs.pop('size')
        return self.line( [ args[0] ], [ args[1] ], *args[2:], **kwargs)



    def draw_lines(self):
        print(len(self.lines), 'lines to draw')
        for args, kwargs in self.lines:
            plt.plot(*args, **kwargs)
        return

    def draw(self):
        self.draw_lines()
        return plt.show()
