import math
import matplotlib
import pandas

import numpy as np
from Scanmethods.FirstLight.random_points import random_predeterment_points
from Scanmethods.Precision.simplex_2d import Simplex_2D
from interface.interfaces import interfaces
from util.point_2D import Point2D
from util.project_root import get_project_root

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


def gridscan(interface, start_location):
    y_begin, z_begin = start_location
    scan_size = 4
    scan_step = 1
    y_index = 0
    z_index = 0
    measured_points = np.full((5, 5), -1.0, dtype=object)
    test = np.full((5, 5), -1.0, dtype=float)
    step_size = 0.1
    for y in np.linspace((y_begin - scan_size / 2), (y_begin + scan_size / 2), scan_size / scan_step + 1,
                         endpoint=True):
        for z in np.linspace(z_begin - scan_size / 2, z_begin + scan_size / 2, scan_size / scan_step + 1,
                             endpoint=True):
            interface.move(y, z)
            measured_points[z_index][y_index] = Point2D((y, z), interface.read())
            test[z_index][y_index] = interface.read()
            z_index += 1
        y_index += 1
        z_index = 0
    sort = np.sort(measured_points, axis=None)
    return test


interface = interfaces()
highest_values = np.full((10, 3), -1.0)
for i in range(0, 15):
    print(highest_values)
    random = random_predeterment_points(interface)
    precision = Simplex_2D(interface)

    highest_location = random.point_scan()
    precision.scan()
    print(precision.get_bestpoint().get_location())
    print(precision.get_bestpoint().get_location())
    highest_values[i][0] = precision.get_bestpoint().point_value
    y, z = precision.get_bestpoint().get_location()
    highest_values[i][1] = y
    highest_values[i][2] = z
    grid = gridscan(interface, precision.get_bestpoint().get_location())
    np.savetxt("Situation " + str(3) + " pullback fiber 11 x extention 30 um gridscan index " + str(i) + ".csv", grid,
               delimiter=",")
    plotsmall(grid, [], precision.get_highest_points(),
              "Situation " + str(3) + " pullback fiber 11 x extention 30 um index " + str(i) + ".png")
    hallo = input('press buton when moved')
    np.savetxt("Situation " + str(3) + " pullback fiber 11 x extention 30 um.csv", highest_values, delimiter=",")
