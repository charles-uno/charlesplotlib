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

    plot = cpl.Plot(rows=1, cols=3)

    plot.title = 'Title'

    plot.xlabel = 'Number of Lands'

    plot.xlims = (12.5, 19.5)
    plot.xticks = (13, 15, 17, 19)

    plot.ylims = (-0.5, 6.5)
    plot.yticks = (0, 2, 4, 6)

    plot.ylabel = 'Number of Cyclers'

    plot.clabels = (
        'Hit 3 land drops',
        'Hit 4 land drops',
        'Hit 5 land drops',
    )

    xvals = 13 + np.arange(8)
    yvals = np.arange(8)
    for i in range(3):
        zvals = 10*np.random.rand(7, 7)

        plot[i].mesh(xvals-0.5, yvals-0.5, zvals)





    return plot.draw()


    fig = cpl.Figure()
    xvals = list( i - 0.5 for i in range(13, 21) )
    yvals = list( i - 0.5 for i in range(0, 8) )

    zvals = 10*np.random.rand(7, 7)

    for i, x in enumerate( xvals[:-1] ):
        for j, y in enumerate( yvals[:-1] ):

            nlands, ncyclers = int(x+0.5), int(y+0.5)

            fig.dots( [x+0.5], [y+0.5], size=35, color='w' )

            zvals[j, i] = curve(4, nlands, ncyclers)*100

            print('with', nlands, 'lands and', ncyclers, 'cyclers:', zvals[i, j])

            fig.text(format(zvals[j, i], '.0f') + '\%', x=x+0.5, y=y+0.5, datacoords=True)
#            fig.text(format(zvals[i, j], '.1f'), x=x+0.5, y=y+0.5, datacoords=True, weight='bold', shadow='w')

#    zvals[1:2, :] = 0


    fig.mesh(xvals, yvals, zvals)

    fig.title('Title')
    fig.xlabel('Number of Lands')

    fig.xlims( (12.5, 19.5) )
    fig.ylims( (-0.5, 6.5) )

    fig.zlims( (0, 100) )


    fig.ylabel('Number of Cyclers')





    return fig.draw('test.png')



    '''
    fig = cpl.Figure(rows=3, cols=3)
    fig.xticks = (13, 15, 17, 19)
    fig.xlabel = 'Horizontal Axis Label'
    fig.ylabel = 'Vertical Axis Label'
    fig.title = 'Figure Title'
    return fig.draw('test.png')
    '''




def curve(nturns, nlands, ncyclers=0):
    # What are the odds of hitting your lands on curve for this many turns on the play?

    # Total number of possible draws.
    ztotal = choose(40 - ncyclers, 6 + nturns)

    # Tally up the odds of getting at least this many lands.
    tally = 0
    for n in range(nturns, 7+nturns):
        z = choose(40 - ncyclers - nlands, 6 + nturns - n)*choose(nlands, n)
        tally += z/ztotal
    return tally




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
    global _seasons
    fig = cpl.Figure()
    seasons = { i:load_season(i) for i in _seasons }

    fig.xlabel('Episode ' + str(n) + ' Technical Rank')
    fig.ylabel('Number of Episodes Survived')
    if n == 1:
        fig.title('Episode 1: Taking Judgments with a Grain of Salt')
    elif n == 2:
        fig.title('Episode 2: Separating the Wheat from the Chaff')



    fig.highlight(xlims=(-99, 3.5), ylims=(-99, 99), color='#006374', alpha=0.15)
    fig.text('Top 3 in\nthis episode', x=0.12, y=0.035)

    fig.highlight(xlims=(-99, 99), ylims=(9.3, 99), color='#006374', alpha=0.15)
    fig.text('Season\nfinalists', x=0.965, y=0.94, rotation=90)



    # Combine all the data into a single list so we can fit it.
    allx, ally = [], []
    # Plot the seasons one at a time, each in a different color.
    for i, season in seasons.items():
        names = sorted( season.keys() )

        # If not looking at the first episode, some of the bakers will
        # not have a score, because they've already been eliminated.
        xarr, yarr = [], []
        for name in names:
            if len( season[name] ) < n:
                continue
            xarr.append( season[name][n-1] )
            yarr.append( len( season[name] ) )

#        color ={
#            3:'#4C72B0',
#            4:'#55A868',
#            5:'#C44E52',
#            6:'#8172B2',
#            7:'#CCB974',
#            8:'#64B5CD',
#        }[i]

        color ={
            3:'#001C7F',
            4:'#017517',
            5:'#8C0900',
            6:'#7600A1',
            7:'#B8860B',
            8:'#006374',
        }[i]

        label = cpl.helpers.tex( 'Series ' + str(i) )
        # Add these values to the big array.
        allx.extend(xarr)
        ally.extend(yarr)
        # After adding to the big array, but before plotting, tweak the
        # values to prevent overlap.
        xarr = [ x + 0.1*pmx(i) for x in xarr ]
        yarr = [ x + 0.1*pmy(i) for x in yarr ]
        fig.dots(xarr, yarr, color=color, label=label)

    # Perform a linear fit, and get an R squared value.
    allx = np.array(allx)
    ally = np.array(ally)
    p = np.polyfit(allx, ally, 1)
    # If we don't sort the values, the line renders poorly.
    xvals = np.array( sorted(allx) )
    yvals = p[0]*xvals + p[1]
    fig.line(xvals, yvals, color='k')
    # Compute R squared, per Wikipedia.
    ybar = np.mean(ally)
    sstot = np.sum( (ally - ybar)**2 )
    ssreg = np.sum( (yvals - ybar)**2 )
    # Stick it in the middle of the plot.
    rlabel = 'R^2\\!=\\!' + format(ssreg/sstot, '.2f')
    fig.text(rlabel)

    plt.xlim( [0.5, 13.5] )
    plt.ylim( [0.5, 10.5] )

    fig.xticks( [1, 4, 7, 10, 13] )
    fig.yticks( [1, 4, 7, 10] )

    return fig.draw('ep' + str(n) + '.svg')

def pmx(i):
    global _seasons
    return np.sin( i*2*np.pi/len(_seasons) )
#    return {3:0, 4:-1, 5:+1}[i]*np.sqrt(0.75)
#    return +1 if i%2 else -1

def pmy(i):
    global _seasons
    return np.cos( i*2*np.pi/len(_seasons) )
#    return {3:np.sqrt(0.75), 4:-0.5, 5:-0.5}[i]
#    return +1 if (i//2)%2 else -1

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
