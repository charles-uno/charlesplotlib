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

def main():
    rows, cols = 1, 3

    landmin, landmax = 11, 19
    cyclemin, cyclemax = 0, 8

    plot = cpl.Plot(rows=rows, cols=cols)
    plot.title = 'Effects of Land Count and Cycling on Mana Curve Reliability'
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
    return plot.draw('curve.png')

# ######################################################################

def curve(hit, miss, nlands, ncyclers=0, draw=False):
    # What are the odds of hitting your lands on curve for this many
    # turns on the play?
    decksize = 40 - ncyclers
    decklands = nlands
    handsize = (7 if draw else 6) + hit
    tally = 1
    for handlands in range(hit):
        tally -= _curve(decksize, decklands, handsize, handlands)
    # Missing your first or second land drop is mutually exclusive with
    # flooding on turn 7, since you only draw 1 land per turn.
    handsize = (7 if draw else 6) + miss
    for handlands in range(miss, handsize + 1):
        tally -= _curve(decksize, decklands, handsize, handlands)
    return tally

# ----------------------------------------------------------------------

def _curve(decksize, decklands, handsize, handlands):
    # Deck size DS, deck lands DL, hand size HS. Return the odds of
    # having exactly HL lands in hand.
    ztotal = choose(decksize, handsize)
    zlands = choose(decksize - decklands, handsize - handlands)
    zspells = choose(decklands, handlands)
    return zlands*zspells/ztotal

# ----------------------------------------------------------------------

def choose(n, k):
    if not 0 <= k <= n:
        return 0
    return math.factorial(n)/( math.factorial(n-k)*math.factorial(k) )

# ######################################################################

if __name__=='__main__':
  main()
