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

    def line(self, *args, **kwargs):
        return self.lines.append( (args, kwargs) )

    def draw_lines(self):
        print(len(self.lines), 'lines to draw')
        for args, kwargs in self.lines:
            plt.plot(*args, **kwargs)
        return

    def draw(self):
        self.draw_lines()
        return plt.show()
