import math
import matplotlib
import pandas

import numpy as np
from piezo.Scanmethods.FirstLight.random_points import random_predeterment_points
from piezo.Scanmethods.Precision.simplex_2d import Simplex_2D
from piezo.Scanmethods.Precision.spiral_scan import Spiral_scan
from piezo.interface.interfaces import interfaces
from piezo.util.point_2D import Point2D
from piezo.util.project_root import get_project_root

matplotlib.use('Agg')

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def fmt(x, pos):
    """"make the notation on the colourbar scientific"""
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)



def plotbig(gridscan, points, simplex_highest=[]):
    y_simplex = []
    z_simplex = []

    y_random = []
    z_random = []
    for point in simplex_highest:
        y, z = point.get_location()
        y_simplex.append(math.floor(y))
        z_simplex.append(math.floor(z))

    for point in points:
        y, z = point.get_location()
        y_random.append(y)
        z_random.append(z)

    fig = plt.figure()
    plt.jet()
    image = plt.imshow(gridscan)
    plt.plot(y_simplex, z_simplex, c='magenta', linewidth=2, label='Simplex path')
    plt.xlabel('Y displacement ${\mu}m$')
    plt.ylabel('Z displacement ${\mu}m$')

    plt.scatter(y_random, z_random, c='r')

    cbar = fig.colorbar(image, format=ticker.FuncFormatter(fmt))
    cbar.ax.set_ylabel('Intensity mA')

    plt.show()


def plotsmall(gridscan, points, simplex_highest, name):
    y_simplex, z_simplex = simplex_highest[-1].get_location()

    y_begin, z_begin = simplex_highest[-1].get_location()

    y_random = []
    z_random = []

    for point in points:
        y, z = point.get_location()
        y_random.append(y)
        z_random.append(z)

    fig = plt.figure()
    plt.jet()
    plt.title("Simplex test optimalisation")
    image = plt.imshow(gridscan, extent=[y_begin - 1 / 2, y_begin + 1 / 2, z_begin - 1 / 2, z_begin + 1 / 2])
    plt.scatter(y_simplex, z_simplex, c='magenta', label='Simplex path')
    plt.xlabel('Y piezo extenion ${\mu}m$')
    plt.ylabel('Z piezo extention ${\mu}m$')

    # plt.scatter(y_random, z_random, c='r')

    cbar = fig.colorbar(image, format=ticker.FuncFormatter(fmt))
    cbar.ax.set_ylabel('Intensity mA')
    plt.savefig(name)
    plt.show()




interface = interfaces()
found_peak = np.empty((10,9), dtype='float')

for i in range(0, 10):
    random = random_predeterment_points(interface)
    precision = Simplex_2D(interface)
    spiral = Spiral_scan(interface)

    spiral.spiral_scan()

    highest_location = random.point_scan()
    precision.scan(highest_location)


    print(precision.get_bestpoint().get_location())
    print(str(precision.get_num_measurements() + random.get_num_measurements()))
    print(spiral.get_bestpoint().get_location())
    print(spiral.get_num_measurements())

    found_peak[i][0] = (precision.get_bestpoint().get_location()[0])
    found_peak[i][1] = (precision.get_bestpoint().get_location()[1])
    found_peak[i][2] = (precision.get_bestpoint().point_value)
    found_peak[i][3] = (precision.get_num_measurements())
    found_peak[i][4] = (random.get_num_measurements())
    found_peak[i][5] = (spiral.get_bestpoint().get_location()[0])
    found_peak[i][6] = (spiral.get_bestpoint().get_location()[1])
    found_peak[i][7] = (spiral.get_bestpoint().point_value)
    found_peak[i][8] = (spiral.get_num_measurements())

    # np.savetxt("Situation " + str(5) + " pullback fiber 6 extention.csv", found_peak, delimiter=",")
