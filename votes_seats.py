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

import plotwrapper

# http://seaborn.pydata.org/_images/color_palettes_8_0.png

# https://github.com/mwaskom/seaborn/blob/master/seaborn/palettes.py

# ######################################################################

def read_array(path, skiplines=1):
    lines = read_lines(path)[skiplines:]
    return np.array([ x.split() for x in lines ], dtype=int)

# ----------------------------------------------------------------------

def read_lines(path):
    with open(path, 'r') as handle:
        return [ x.rstrip() for x in handle ]

# ======================================================================

def make_step(years, seats):
    # NOTE -- We have the most recent year first.
    _years, _seats = years[::-1], seats[::-1]
    y = [_years[0]]
    for year in _years[1:]:
        y.append(year), y.append(year)
    gap = abs( _years[1] - _years[0] )
    y.append(_years[-1] + gap)
    s = []
    for seat in _seats:
        s.append(seat), s.append(seat)
    return np.array(y), np.array(s)







def main():


    house = read_array('votes_seats/house.txt')
    senate = read_array('votes_seats/senate.txt')
    potus = read_array('votes_seats/potus.txt')

    # Array columns: year, dem seats, gop seats, dem votes, gop votes
    hy = house[:, 0]
    hs_dem = house[:, 1]
    hs_gop = house[:, 2]
    hs_tot = hs_dem + hs_gop
    hv_dem = house[:, 3]
    hv_gop = house[:, 4]
    hv_tot = hv_dem + hv_gop

    # "Seats" in the electoral college.
    ey = potus[:, 0]
    es_dem = potus[:, 1]
    es_gop = potus[:, 2]
    es_tot = es_dem + es_gop
    ev_dem = potus[:, 3]
    ev_gop = potus[:, 4]
    ev_tot = ev_dem + ev_gop

    # Senate votes are a bit tricky, since they are staggered into three
    # classes. The senate in 2017 is from the votes in 2012, 2014, and
    # 2016. So let's roll the votes arrays to get the effective popular
    # vote.
    sv_dem_1 = senate[:, 3]
    sv_gop_1 = senate[:, 4]
    sv_dem_2 = np.roll(sv_dem_1, -1)
    sv_dem_3 = np.roll(sv_dem_2, -1)
    sv_gop_2 = np.roll(sv_gop_1, -1)
    sv_gop_3 = np.roll(sv_gop_2, -1)
    # Because of the rolling, we need to chop off our last 2 data points
    # from the senate data.
    sv_dem = (sv_dem_1 + sv_dem_2 + sv_dem_3)[:-2]
    sv_gop = (sv_gop_1 + sv_gop_2 + sv_gop_3)[:-2]
    sv_tot = sv_dem + sv_gop

    sy = senate[:, 0][:-2]

    ss_dem = senate[:, 1][:-2]
    ss_gop = senate[:, 2][:-2]
    ss_tot = ss_dem + ss_gop

    plot = plotwrapper.Plot(rows=1, cols=2)
    plot.title('GOP Vote Share (red) and Resulting Seat Share (white)')

    plot.collabels('House', 'Senate')
#    plot.collabels('House', 'Senate', 'Electoral College')

    plot.ylims( [0.3, 0.7] )
    yticks = [0.3, 0.4, 0.5, 0.6, 0.7]
    yticklabels = [ '%.0f\%%' % (100*x) for x in yticks ]
    plot.yticks(yticks)
    plot.yticklabels(yticklabels)
    plot.ylabel('Representation')

    plot.xlims( [1944, 2018] )
    xticks = [1944, 1952, 1960, 1968, 1976, 1984, 1992, 2000, 2008, 2016]
    plot.xticks(xticks)
    plot.xticklabels(xticks)
    plot.xlabel('Election Year')

    gop_color = 'C3'
    dem_color='C0'

    plot[0].bar(hy, hv_gop/hv_tot, label='GOP Votes', width=2, align='edge', color=gop_color)
    plot[0].bar(hy, -hv_dem/hv_tot, label='Dem Votes', width=2, align='edge', color=dem_color, bottom=1)
    plot[0].line(*make_step(hy, hs_gop/hs_tot), label='Seats', color='white')

    plot[1].bar(sy, sv_gop/sv_tot, label='GOP Votes', width=2, align='edge', color=gop_color)
    plot[1].bar(sy, -sv_dem/sv_tot, label='Dem Votes', width=2, align='edge', color=dem_color, bottom=1)
    plot[1].line(*make_step(sy, ss_gop/ss_tot), label='Seats', color='white')

#    plot[2].bar(ey, ev_gop/ev_tot, label='GOP Votes', width=4, align='edge', color=gop_color)
#    plot[2].bar(ey, -ev_dem/ev_tot, label='Dem Votes', width=4, align='edge', color=dem_color, bottom=1)
#    plot[2].line(*make_step(ey, es_gop/es_tot), label='Seats', color='white')

    plot[0].line([1776, 2024], [0.5, 0.5], color='k', ls=':')
    plot[1].line([1776, 2024], [0.5, 0.5], color='k', ls=':')
#    plot[2].line([1776, 2024], [0.5, 0.5], color='k', ls=':')

    return plot.draw('votes_seats.png')















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
