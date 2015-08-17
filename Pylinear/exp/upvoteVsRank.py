'''Plots the number of updates an answer recieves versus its absolute (1,2,3...) and relative ((n-i)/n) ranks.'''
from __future__ import division
from Pylinear.feature import getDataFiles
import re
import json

# (abs, rel, votes)
def plot(points):
    from matplotlib import pyplot as plt

    '''
    f, axarr = plt.subplots(2)

    ps = [(i[0], i[2]) for i in points]
    axarr[0].scatter(*zip(*ps))
    axarr[0].set_title("Absolute Rank")
    axarr[0].set_xlabel("Rank")
    axarr[0].set_ylabel("Upvotes")
    axarr[0].set_xlim([-1,None])
    axarr[0].set_ylim([-500,None])

    ps = [(i[1], i[2]) for i in points]
    axarr[1].scatter(*zip(*ps))
    axarr[1].set_title("Relative Rank")
    axarr[1].set_xlabel("Rank")
    axarr[1].set_ylabel("Upvotes")
    axarr[1].set_xlim([-0.05,1.05])
    axarr[1].set_ylim([-500,None])
    '''
    ps = [(i[0], i[2]) for i in points if i[2] != 0]
    plt.scatter(*zip(*ps))
    plt.yscale('log')
    plt.title("Absolute Rank")
    plt.xlabel("Rank")
    plt.ylabel("Upvotes")
    plt.ylim([0,None])
    plt.show()

    ps = [(i[1], i[2]) for i in points if i[2] != 0]
    plt.scatter(*zip(*ps))
    plt.yscale('log')
    plt.title("Relative Rank")
    plt.xlabel("Rank")
    plt.ylabel("Upvotes")
    plt.ylim([0,None])
    plt.show()

    #plt.tight_layout()
    #plt.show()

def getData():
    answerVals = []
    points = []
    numAnswers = 0
    lastThread = ""
    first = True
    path = '/export/a04/wpovell/splits/train'
    #path = 'splits/train/data'
    for n, f in getDataFiles(path):
        split = n.split("/")
        thread = split[1]
        fn = split[2]

        if first:
            first = False
            lastThread = thread
        elif thread != lastThread:
            for i in answerVals:
                points.append((i[0], (numAnswers-i[0])/numAnswers, i[1]))
            answerVals = []
            numAnswers = None
            lastThread = thread

        if fn.endswith('metadata.json'):
            data = json.load(f)
            numAnswers = data['numAnswers']

        rank = re.findall(r'answer(\d+)\.json', fn)
        if rank:
            rank = int(rank[0])
            data = json.load(f)
            answerVals.append((rank, data['upvotes']))
    return points

if __name__ == '__main__':
    #points = getData()
    with open('upvotePlot.dat') as f:
        points = json.load(f)
    plot(points)