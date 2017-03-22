#!/usr/bin/env python3

# ######################################################################

import matplotlib.pyplot as plt

# ######################################################################

def main():

    data = load_season(3)

    for name, scores in data.items():
        print(name, '\t', scores)

    for name, scores in data.items():

        xvals = range(1, len(scores)+1)

        plt.plot(xvals, scores, label=name)

    plt.axis([0, 12, 0, 12])
    plt.show()

    return



# ######################################################################

def load_season(n):
    scores = {}
    for line in read('s' + str(n) + '.txt'):
        # Skip spacer lines. We don't need to explicitly track episodes,
        # since each baker appears exactly once in each.
        if not line:
            continue
        name, score = line.split()
        if name not in scores:
            scores[name] = []
        scores[name].append( int(score) )
    return scores

# ----------------------------------------------------------------------

def read(filename):
    with open(filename, 'r') as handle:
        return [ x.rstrip() for x in handle ]

# ######################################################################

if __name__ == '__main__':
    main()
