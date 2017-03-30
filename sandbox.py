#!/usr/bin/env python3

# Charles McEachern

# Spring 2016

# Example driver for the Charlesplotlib plotting library.

# ######################################################################

import numpy as np
import os
import random
import sys

import charlesplotlib as cpl

# ######################################################################

def main():

    return gbbo(2)

    return scratch()

    return contour()



# ----------------------------------------------------------------------

import matplotlib.pyplot as plt

import cubehelix


def scratch():

    '''
    This syntax looks nice, I think:

    fig.title = 'Title'
    fig.xlabel = 'Horizontal Axis Label'
    fig.xmin, fig.xmax = 1, 100
    fig.xlog = True
    fig.ncolors = 13
    fig.nticks = 5

    What all do we need?

    title
    xlabel, ylabel
    zlabel/zunits
    xmin, xmax, xlog
    ymin, ymax, ylog
    zmin, zmax, zlog
    xticks, yticks, zticks
    (labels are formatted nicely automatically)

    Maybe print a warning if nticks doesn't divide nicely into ncolors?

    Nice-looking plots have ticks at integers. That seems like a safe assumption for the x and y axes.

    How about the z axis?

    How about handling of log axes?

    Come up with a sample bullseye plot.
    '''
    fig = cpl.Figure()
    n = 5
    xvals = list( range(n) )
    yvals = list( range(n) )
    zvals = 10*np.random.rand(n, n)
    fig.mesh(xvals, yvals, zvals)
    fig.title('Title')
    fig.xlabel('Horizontal Axis Label')
    fig.ylabel('Vertical Axis Label')
    return fig.draw('test.png')



def gbbo(n):
    fig = cpl.Figure()
    seasons = { i:load_season(i) for i in (2, 3, 4, 5) }
    fig.xlabel('Episode ' + str(n) + ' Technical Rank')
    fig.ylabel('Number of Episodes Survived')
    cmap = cpl.helpers.seq_cmap()
    # Combine all the data into a single list so we can fit it.
    allranks, allepisodes = [], []
    # Plot the seasons one at a time, each in a different color.
    for i, season in seasons.items():
        names = sorted( season.keys() )
        # If not looking at the first episode, some of the bakers will
        # not have a score, because they've already been eliminated.
        ranks, episodes = [], []
        for name in names:
            if len( season[name] ) < n:
                continue
            ranks.append( season[name][n-1] )
            episodes.append( len( season[name] ) )
        color = ('k', 'y', 'r', 'b', 'g', 'm', 'c')[i]
        ranks = [ x + 0.1*pmx(i) for x in ranks ]
        episodes = [ x + 0.1*pmy(i) for x in episodes ]
        label = cpl.helpers.tex( 'Series ' + str(i) )
        fig.dots(ranks, episodes, color=color, label=label)
        allranks.extend(ranks)
        allepisodes.extend(episodes)
    # Perform a linear fit, and get an R squared value.
    allranks = np.array(allranks)
    allepisodes = np.array(allepisodes)
    p = np.polyfit(allranks, allepisodes, 1)
    # If we don't sort the values, the line renders poorly.
    xvals = np.array( sorted(allranks) )
    yvals = p[0]*xvals + p[1]
    fig.line(xvals, yvals, color='k')
    # Compute R squared, per Wikipedia.
    ybar = np.mean(allepisodes)
    sstot = np.sum( (allepisodes - ybar)**2 )
    ssreg = np.sum( (yvals - ybar)**2 )
    # Stick it in the middle of the plot.
    rlabel = 'R^2\\!=\\!' + format(ssreg/sstot, '.2f')
    fig.text(rlabel)

    if n == 1:
        fig.title('Episode 1: No Particular Correlation')
    elif n == 2:
        fig.title('Episode 2: Cream Rises to the Top')
#        fig.title('Episode 2: Now with $p$-Hacking')

    plt.xlim( [0.5, 13.5] )
    plt.ylim( [0.5, 10.5] )

    fig.xticks( [1, 4, 7, 10, 13] )
    fig.yticks( [1, 4, 7, 10] )

    return fig.draw('ep' + str(n) + '.png')

def pmx(i):
    return +1 if i%2 else -1

def pmy(i):
    return +1 if (i//2)%2 else -1

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
        if score.isdigit():
            score = int(score)
        else:
            score = 5.5
        scores[name].append(score)
    return scores









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



def contour():

    # Let's do four plots.

    # For each, figure out the domain. Magnitude no greater than 10.
    # Each minimum has a 1 in 4 chance of being negative (so they will
    # all four be positive decently often).

    xlims = [ lims(1000) for _ in range(4) ]
    ylims = [ lims(1000) for _ in range(4) ]

    n = 5

    pw = cpl.plotwindow(2, 2, slope=1.)

    xvals = [ np.linspace(x[0], x[1], n) for x in xlims ]
    yvals = [ np.linspace(y[0], y[1], n) for y in ylims ]

    pw[0].mesh( xvals[0], yvals[0], zvals(n) )
    pw[1].contour( xvals[1], yvals[1], zvals(n) )
    pw[2].contour( xvals[2], yvals[2], zvals(n) )
    pw[3].mesh( xvals[3], yvals[3], zvals(n) )

    clabs = ('row 0 $w^2 = \\sqrt{b}$ test', 'row 1')

    rlabs = ('$m = 1$', '$m = 4$')

    pw.style(clabs=clabs, rlabs=rlabs, title='ABCD sample title')

    if flip():
        pw.style(xlog=True)
    else:
        pw.style(ylog=True)

    if flip():
        pw.style(zlog=True)

    pw.draw()

    return








    pw = cpl.plotwindow(1, 2, slope=1.)

    n = 5

    x = np.linspace(3, 8, n)
    y = np.linspace(0, 10, n)
    scale = np.random.randint(100)
    if flip():
        z = scale*np.random.rand(n, n)
    else:
        z = 2*scale*np.random.rand(n, n) - scale
    pw[0].contour(x, y, z)

    x = np.linspace(0, 10, n+1)
    y = np.linspace(2, 7, n+1)
    scale = np.random.randint(100)
    if flip():
        z = scale*np.random.rand(n, n)
    else:
        z = 2*scale*np.random.rand(n, n) - scale
    pw[1].mesh(x, y, z)

    clabs = ('row 0 $w^2 = \\sqrt{b}$ test', 'row 1')
    pw.style(clabs=clabs, title='ABCD sample title')

    pw.draw()

    return






# ######################################################################
# #################################################### For Importability
# ######################################################################

if __name__=='__main__':
  main()
