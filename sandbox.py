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

def flip():
  return np.random.randint(2)==0



def contour():

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


