#!/usr/bin/env python3

# Charles McEachern

# Spring 2016

# ######################################################################
# ############################################################# Synopsis
# ######################################################################

# Example driver for the Charlesplotlib plotting library. 

# ######################################################################
# ################################################## Load Python Modules
# ######################################################################

import charlesplotlib as cpl
import numpy as np

# ######################################################################
# ################################################################# Main
# ######################################################################

def main():

    return contour()


# ######################################################################
# ######################################################### Contour Plot
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
    # Each minimum has a 1 in 4 chancce of being negative (so they will
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


