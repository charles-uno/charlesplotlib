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

# ======================================================================

def state_name(line):
    words = line.split()
    if words[0] == words[1] or not words[1][0].isalpha():
        return words[0]
    else:
        return words[0] + ' ' + words[1]


def main():

    with open('votes_seats/raw_white_pop.txt', 'r') as handle:
        vals = [ x.rstrip().replace(',', '').split('\t') for x in handle ]

    lines = []

    for val in vals:

        name = state_name(val[0])

        if len(val) < 8 or not val[8].strip():
            print('skipping:', name)
            continue

        pct = float( val[8].rstrip('%') )
        lines.append(name + '\t' + str(pct))

        print(pct, '\t', name)

    with open('votes_seats/pct_white.txt', 'w') as handle:
        [ handle.write(x + '\n') for x in sorted(lines) ]


    return





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

    collabels = 'House', 'Senate' #, 'Electoral College'

    plot = plotwrapper.Plot(rows=1, cols=len(collabels))
    plot.title('GOP Vote Share (Red) and Resulting Seat Share (White)')

    plot.collabels(*collabels)

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

    years = [hy, sy, ey]
    votes = [hv_gop/hv_tot, sv_gop/sv_tot, ev_gop/ev_tot]
    seats = [hs_gop/hs_tot, ss_gop/ss_tot, es_gop/es_tot]



    for i, (y, v, s) in enumerate( zip(years, votes, seats) ):

        if i == 1:

            for year, vote, seat in zip(y, v, s):
                print(year, ':', '%.1f' % (100*vote), '', '%.1f' % (100*seat))
            return




        if i == len(collabels):
            break

#        plot[i].bar(y, v, label='GOP Votes', width=2, align='edge', color=gop_color)
#        plot[i].bar(y, v - 1, label='Dem Votes', width=2, align='edge', color=dem_color, bottom=1)
#        plot[i].line(*make_step(y, s), label='Seats', color='white')


        plot[i].line(*make_step(y, v), label='Votes', color='red')
        plot[i].line(*make_step(y, s), label='Seats', color='black')



#        _y, _v = make_step(y, v)
#        _y, _s = make_step(y, s)
#        plot[i].line(_y, _v, label='Votes', color='red')
#        plot[i].line(_y, _s, label='Seats', color='black')
#        plot[i].fill_between(_y, _v, _s, where=_v>_s, facecolor='green', interpolate=True)

        plot[i].line([1776, 2024], [0.5, 0.5], color='k', ls=':')

    return plot.draw('votes_seats.png')


# ######################################################################

if __name__=='__main__':
  main()
