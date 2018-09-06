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

    return gbbo(1)








def scratch():

    fig = cpl.Figure()

    items = list( load_season(1).items() ) + list( load_season(2).items() ) + list( load_season(3).items() )

    def sortkey(x):
        return x[1][0]
    items = sorted(items, key=sortkey)

    for name, scores in items:
        print(name, '\t', scores)

    cmap = cubehelix.cmap(
        startHue=0,
        endHue=600,
        minSat=1,
        maxSat=2.5,
        minLight=0.2,
        maxLight=0.8,
    )

    fig.xlabel('Episode 1 Technical Rank')
    fig.ylabel('Number of Episodes Survived')

    for i, (name, scores) in enumerate(items):
        xvals = range(1, len(scores)+1)
        color = cmap( i*1./(len(items)+1) )
        fig.mark(scores[0], len(scores), size=12, color=color)

    nepisodes = max( len(s) for n, s in items )
    nbakers = max( s[0] for n, s in items )
    plt.xlim( [0.5, nepisodes + 0.5] )
    plt.ylim( [0.5, nbakers + 0.5] )

    return fig.draw()






    cmap = cpl.helpers.seq_cmap()

#    cmap = plt.get_cmap('plasma')

    for i, (name, scores) in enumerate(items):
        xvals = range(1, len(scores)+1)
        color = cmap( i*1./(len(items)+1) )
        fig.line(xvals, scores, color=color, label=name, linewidth=3)

    for i, (name, scores) in enumerate(items):
        xvals = range(1, len(scores)+1)
        color = cmap( i*1./(len(items)+1) )
        fig.line(xvals, scores, linestyle='None', marker='o', markersize=12, color=color, markeredgecolor=color)

    xmax = max( len(s) for n, s in items )
    ymax = len(items)

    plt.xlim( [0.5, xmax + 0.5] )
    plt.ylim( [0.5, ymax + 0.5] )


    return fig.draw()













# ######################################################################

def flip(n=2):
    """Returns True one time out of n (default 2)."""
    return np.random.randint(n)==0

def lims(scalemax):
    maybe_min = np.random.randint(scalemax)
#    if flip(4):
#        maybe_min *= -1
    maybe_max = np.random.randint(scalemax)
    return sorted( [maybe_min, maybe_max] )


def zvals(n, scalemax=1000):
    scale = np.random.randint(scalemax)
    # One time in four, make it negative.
    if flip(4):
        return 2*scale*np.random.rand(n, n) - scale
    else:
        return scale*np.random.rand(n, n)





# ######################################################################

def load_season(n):
    scores = {}
    for line in cpl.helpers.read('gbbo/s' + str(n) + '.txt'):
        # Skip spacer lines. We don't need to explicitly track episodes,
        # since each baker appears exactly once in each.
        if not line:
            continue
        name, score = line.split()
        if name not in scores:
            scores[name] = []
        if not score.isdigit():
            score = 5.5
        scores[name].append( int(score) )
    return scores

# ######################################################################

if __name__=='__main__':
  main()
