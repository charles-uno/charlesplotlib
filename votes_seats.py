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

def defaultdictdict(t):
    return collections.defaultdict(lambda: collections.defaultdict(t))

# ----------------------------------------------------------------------

def load_data():
    data = defaultdictdict(int)

    for chamber in ('house', 'senate'):
        for metric in ('votes', 'seats'):
            tally_key = chamber + '_' + metric

            for party in ('dem', 'gop'):
                key = chamber + '_' + metric + '_' + party
                for line in read_lines('votes_seats/%s.txt' % key):

                    try:
                        year, val = [ int(x) for x in line.split() ]
                    except ValueError:
                        continue

                    data[year][key] = val
                    data[year][tally_key] += val

    return data

# ----------------------------------------------------------------------

def read_lines(path):
    with open(path, 'r') as handle:
        return [ x.rstrip() for x in handle ]

# ======================================================================

def main():

    data = load_data()



    with open('votes_seats/senate.txt', 'w') as handle:

        handle.write( '\t'.join( ('year', 'ssd', 'ssr', 'svd', 'svr') ) + '\n')

        for year, year_data in sorted(data.items(), reverse=True):

            handle.write( '\t'.join( str(x) for x in (year, year_data['senate_seats_dem'], year_data['senate_seats_gop'], year_data['senate_votes_dem'], year_data['senate_votes_gop']) ) + '\n')

    return







#    [ print(k, ':', v) for k, v in sorted( data.items() ) ]

    years = []
    house_vote_shares, house_seat_shares = [], []
    senate_vote_shares, senate_seat_shares = [], []

    senate_vote_top, senate_vote_bot = [], []

    for year, year_data in sorted( data.items() ):
        years.append(year)
        house_vote_shares.append(
            year_data['house_votes_gop']/year_data['house_votes']
        )
        house_seat_shares.append(
            year_data['house_seats_gop']/year_data['house_seats']
        )

        if year_data['senate_seats']:
            senate_seat_shares.append(
                year_data['senate_seats_gop']/year_data['senate_seats']
            )
        else:
            senate_seat_shares.append(0)

        senate_vote_top.append( year_data['senate_votes_gop'] )
        senate_vote_bot.append( year_data['senate_votes'] )

    # Senate terms are six years, so the 2017 senate is from the 2012, 2014, and 2016 elections.

    while len(senate_vote_top) > 2:

        vote_top = sum(senate_vote_top[:3])
        vote_bot = sum(senate_vote_bot[:3])

        senate_vote_top.pop(0)
        senate_vote_bot.pop(0)

        if vote_bot:
            senate_vote_shares.append(vote_top/vote_bot)
        else:
            senate_vote_shares.append(0)









    plot = cpl.Plot(rows=1, cols=2)
    plot.title = 'GOP Vote and Seat Shares'

    plot.clabels = 'House', 'Senate'

    plot.xlabel = 'Year'
    plot.ylabel = 'Share'

    plot.ylims = 0.3, 0.7
    plot.yticks = 0.3, 0.4, 0.5, 0.6, 0.7
    plot.yticklabels = '30\%', '40\%', '50\%', '60\%', '70\%'

    plot.xlims = 1938, 2016
#    plot.xticks = 1984, 1992, 2000, 2008, 2016


    plot[0].line(years, house_vote_shares, label='GOP Votes')
    plot[0].line(years, house_seat_shares, label='GOP Seats')
    plot[0].line([0, 3000], [0.5, 0.5], color='k', ls=':')

    plot[1].line(years[2:], senate_vote_shares, label='GOP Votes')
    plot[1].line(years, senate_seat_shares, label='GOP Seats')
    plot[1].line([0, 3000], [0.5, 0.5], color='k', ls=':')


    return plot.draw('votes_seats.png')






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

# ######################################################################

if __name__=='__main__':
  main()
