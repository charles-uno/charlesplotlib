#!/usr/bin/env python3

r'''

import matplotlib
import matplotlib.pylab as plt


matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = 'Computer Modern'
matplotlib.rcParams['text.usetex'] = True

#rc('font', **{'family': 'sans-serif'})
#rc('mathtext', **{'fontset':'custom', 'rm':'Bitstream Vera Sans', 'it':'Bitstream Vera Sans:italic', 'bf':'Bitstream Vera Sans:bold'})

matplotlib.rcParams['text.latex.preamble'] = [
       r'\usepackage{helvet}',    # set the normal font here
       r'\usepackage{sansmath}',  # load up the sansmath so that math -> helvet
       r'\sansmath'               # <- tricky! -- gotta actually tell tex to use!
]


#matplotlib.rcParams['mathtext.fontset'] = 'cm'
#matplotlib.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
#matplotlib.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
#matplotlib.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'


#rc('text', usetex=True)

x = plt.linspace(0,5)
plt.plot(x,plt.sin(x))
plt.ylabel(r"This is $\sin(x)$", size=20)
plt.show()

exit()

'''











# Charles McEachern

# Spring 2016

# Example driver for the Charlesplotlib plotting library.

# ######################################################################

import numpy as np
import os
import random
import sys

import charlesplotlib as cpl


# http://seaborn.pydata.org/_images/color_palettes_8_0.png

# https://github.com/mwaskom/seaborn/blob/master/seaborn/palettes.py


# ######################################################################

_seasons = (3, 4, 5, 6, 7)

def main():



    return cyclers()



    return gbbo(1)

    return scratch()

    return contour()


# ----------------------------------------------------------------------

def cyclers():

    rows, cols = 2, 3

    landmin, landmax = 13, 19
    cyclemin, cyclemax = 0, 6

    plot = cpl.Plot(rows=rows, cols=cols)
    plot.title = 'Effects of Land Count and Cycling on Mana Curve Reliability'
    plot.xlabel = 'Number of Lands'

    plot.xlims = landmin - 0.5, landmax + 0.5
    plot.ylims = cyclemin - 0.5, cyclemax + 0.5

    plot.xticks = range(landmin, landmax + 1, 2)
    plot.yticks = range(cyclemin, cyclemax + 1, 2)
    plot.zticks = 10, 30, 50, 70, 90

    plot.zticklabels = [ str(x) + '\%' for x in plot.zticks ]

    plot.ncolors = 21

    plot.ylabel = 'Number of Cards with Cycling'

    plot.clabels = (
        'Hit 3$^{\mathrm{rd}}$ land but not 7$^{\mathrm{th}}$',
        'Hit 4$^{\mathrm{th}}$ land but not 8$^{\mathrm{th}}$',
        'Hit 5$^{\mathrm{th}}$ land but not 9$^{\mathrm{th}}$',

#        'Hit 5th land but not 9th',

#        '\\geq\\!3 lands on turn 3, <\\!7 lands on turn 7',
#        '\\geq\\!4 lands on turn 4, <\\!8 lands on turn 8',
#        '\\geq\\!5 lands on turn 5, <\\!9 lands on turn 9',
    )

    plot.rlabels = ('Play', 'Draw')

    xvals = np.arange(landmin, landmax + 2)
    yvals = np.arange(cyclemin, cyclemax + 2)
    for col in range(cols):

        for row in range(rows):

            zvals = np.random.rand(cyclemax - cyclemin + 1, landmax - landmin + 1)

            for i, x in enumerate( xvals[:-1] ):
                for j, y in enumerate( yvals[:-1] ):

                    tmp = curve(3 + col, 7 + col, x, ncyclers=y, draw=row)*100
                    zvals[j, i]  = tmp

                    if i%2 == 0 and j%2 == 0:
#                        plot[row, col].dots( [x], [y], size=20, color='w' )
                        plot[row, col].text(format(tmp, '.0f') + '\%', x=x, y=y)

            plot[row, col].mesh(xvals-0.5, yvals-0.5, zvals)

    return plot.draw('curve.png')








def curve(hit, miss, nlands, ncyclers=0, draw=False):
    # What are the odds of hitting your lands on curve for this many turns on the play?

    decksize = 40 - ncyclers
    decklands = nlands
    handsize = (7 if draw else 6) + hit

    tally = 0
    for handlands in range(hit, hit + 7):

        # Odds to hit 3+ lands on turn 3
        tohit = _curve(decksize, decklands, handsize, handlands)

        # Odds that from there, you have NOT hit 8 lands on turn 8
        tomiss = 0
        deckleft = decksize - handsize
        landsleft = decklands - handlands
        newhand = miss - hit
        for newlands in range(0, miss - handlands):
            tomiss += _curve(deckleft, landsleft, newhand, newlands)

        tally += tohit*tomiss

    return tally




def _curve(decksize, decklands, handsize, handlands):
    # Deck size DS, deck lands DL, hand size HS. Return the odds of having exactly HL lands in hand.
    ztotal = choose(decksize, handsize)
    zlands = choose(decksize - decklands, handsize - handlands)
    zspells = choose(decklands, handlands)
    return zlands*zspells/ztotal



def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok, ktok = 1, 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0



# ######################################################################
# #################################################### For Importability
# ######################################################################

if __name__=='__main__':
  main()
