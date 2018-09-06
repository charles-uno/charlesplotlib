#!/usr/bin/env python3


# Charles McEachern

# Spring 2016

# Example driver for the Charlesplotlib plotting library.

# ######################################################################

import collections
import math
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



#    return valakut()



#    return print('5 choose 2', choose(5, 2))


    return cyclers()



    return gbbo(1)

    return scratch()

    return contour()





def valakut():

    valakut_data('matthias')

    plot = cpl.Plot(rows=1, cols=2)
    plot.title = 'Titan Breach'
    plot.xlabel = 'Turn'

    plot.xlims = 1, 10
    plot.ylims = 0, 50

    plot.xticks = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    plot.xticklabels = '1', '', '', '4', '', '', '7', '', '', '10'

    plot.yticks = [ 10*x for x in range(11) ]
    # 0, 20, 40, 60, 80, 100
    yticklabels = [ str(x) + '\\%' for x in plot.yticks ]
    plot.yticklabels = [ '' if i%2 else x for i, x in enumerate(yticklabels) ]

    #'0\\%', '20\\%', '40\\%', '60\\%', '80\\%', '100\\%'

    plot.ylabel = 'Cumulative Odds of Making Titan'

    plot.clabels = 'On the Play', 'On the Draw'

    for xval in range(1, 11):
        [ plot[i].line([xval, xval], [0, 100], linestyle=':', color='gray') for i in range(2) ]

    for yval in range(0, 101, 10):
        [ plot[i].line([0, 10], [yval, yval], linestyle=':', color='gray') for i in range(2) ]



    for name in ('netdeck', 'matthias', 'explore'):

        color = {'netdeck':'b', 'matthias':'r', 'explore':'g'}[name]
        label = {'netdeck':'Zach', 'matthias':'Matthias', 'explore':'Charles'}[name]

        play = valakut_data(name, play=True)
        plot[0].line(play[0], play[1], label=label, color=color)

        draw = valakut_data(name, play=False)
        plot[1].line(draw[0], draw[1], label=label, color=color)

    return plot.draw('out.png')



def valakut_names():
    files = os.listdir('/home/charles/Desktop/valakut/data/')
    files = [ x for x in files if x.endswith('.dat') ]
    return { x[:x.rfind('-')] for x in files }


def valakut_data(name, play=True):
    ext = '-' + ('play' if play else 'draw') + '.dat'
    path = '/home/charles/Desktop/valakut/data/' + name + ext
    vals = collections.defaultdict(int)
    with open(path, 'r') as handle:
        for line in handle:
            vals[ int(line) ] += 1
    total = sum( vals.values() )

#    [ print(k, ':', v*100./total) for k, v in vals.items() ]

    turns, probs = [], []
    for turn, n in sorted( vals.items() ):

        cumulative = 0
        # Turn = -1 is used to indicate killed jobs.
        if turns and turns[-1] > 0:
            cumulative = probs[-1]

        turns.append(turn)
        probs.append( cumulative + n*100./total )

    return turns, probs






# ----------------------------------------------------------------------

def cyclers():

    rows, cols = 1, 3

    landmin, landmax = 11, 19
    cyclemin, cyclemax = 0, 8

    plot = cpl.Plot(rows=rows, cols=cols)
    plot.title = 'Effects of Land Count and Cycling on Mana Curve Reliability'
#    plot.title = 'How Lands and Cyclers affect Curve Reliability'
    plot.xlabel = 'Number of Lands'

    plot.xlims = landmin - 0.5, landmax + 0.5
    plot.ylims = cyclemin - 0.5, cyclemax + 0.5

    plot.xticks = range(landmin, landmax + 1, 2)
    plot.yticks = range(cyclemin, cyclemax + 1, 2)
    plot.zticks = 10, 30, 50, 70, 90

    plot.zticklabels = [ str(x) + '\%' for x in plot.zticks ]

    plot.ncolors = 29

    plot.ylabel = 'Number of Cards with Cycling'

    plot.clabels = (
#        'Hit 3$^{\mathrm{rd}}$ land but not 7$^{\mathrm{th}}$',
#        'Hit 4$^{\mathrm{th}}$ land but not 8$^{\mathrm{th}}$',
#        'Hit 5$^{\mathrm{th}}$ land but not 9$^{\mathrm{th}}$',

#        'Hit 5th land but not 9th',

        '$\\geq\\!3$ lands on turn 3 and $<\\!7$ lands on turn 7',
        '$\\geq\\!4$ lands on turn 4 and $<\\!8$ lands on turn 8',
        '$\\geq\\!5$ lands on turn 5 and $<\\!9$ lands on turn 9',
    )

    plot.rlabels = ('Play', 'Draw')

    xvals = np.arange(landmin, landmax + 2)
    yvals = np.arange(cyclemin, cyclemax + 2)
    for col in range(cols):

        zvals = np.random.rand(cyclemax - cyclemin + 1, landmax - landmin + 1)

        for i, x in enumerate( xvals[:-1] ):
            for j, y in enumerate( yvals[:-1] ):

                zplay = curve(3 + col, 7 + col, x, ncyclers=y, draw=False)*100

                zdraw = curve(3 + col, 7 + col, x, ncyclers=y, draw=True)*100

                zvals[j, i] = 0.5*(zplay + zdraw)

                if i%2 == 0 and j%2 == 0:
                    plot[col].text(format(zvals[j, i], '.0f') + '\%', x=x, y=y, fontsize=16)

            plot[col].mesh(xvals-0.5, yvals-0.5, zvals)

        continue

        for row in range(rows):
            for i, x in enumerate( xvals[:-1] ):
                for j, y in enumerate( yvals[:-1] ):
                    tmp = curve(3 + col, 7 + col, x, ncyclers=y, draw=row)*100
                    zvals[j, i]  = tmp
                    if i%2 == 0 and j%2 == 0:
                        plot[row, col].text(format(tmp, '.0f') + '\%', x=x, y=y)
            plot[row, col].mesh(xvals-0.5, yvals-0.5, zvals)

    return plot.draw('curve.png')








def curve(hit, miss, nlands, ncyclers=0, draw=False):
    # What are the odds of hitting your lands on curve for this many turns on the play?
    decksize = 40 - ncyclers
    decklands = nlands
    handsize = (7 if draw else 6) + hit
    tally = 1
    for handlands in range(hit):
        tally -= _curve(decksize, decklands, handsize, handlands)
    # Missing your first or second land drop is mutually exclusive with flooding on turn 7, since you only draw 1 land per turn.
    handsize = (7 if draw else 6) + miss
    for handlands in range(miss, handsize + 1):
        tally -= _curve(decksize, decklands, handsize, handlands)
    return tally



def _curve(decksize, decklands, handsize, handlands):
    # Deck size DS, deck lands DL, hand size HS. Return the odds of having exactly HL lands in hand.

    ztotal = choose(decksize, handsize)
    zlands = choose(decksize - decklands, handsize - handlands)
    zspells = choose(decklands, handlands)
    return zlands*zspells/ztotal


def choose(n, k):
    if not 0 <= k <= n:
        return 0
    return math.factorial(n)/( math.factorial(n-k)*math.factorial(k) )


# ######################################################################
# #################################################### For Importability
# ######################################################################

if __name__=='__main__':
  main()
