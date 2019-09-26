import os
import shutil
import time

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm

import numpy as np


def fmt(x, pos):
    """"make the notation on the colourbar scientific"""
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)


def reformattime():
    """returns the time in UTC defined as year-month-day-hour:minute:second. Time is the UTC time"""
    return time.strftime("%Y-%m-%d-%H,%M,%S-UTC-Grindscan.png", time.gmtime())


def plot2D(data, step_time, fiber, name=None):
    """"plots and array of data on a 2d image with a colourwheel"""
    if name is None:
        name = reformattime()

    # setup the settings for the plot
    fig = plt.figure()
    plt.title('Grid scan test intensity (W) step time: ' + str(step_time) + "s" + " fiber" + str(fiber))
    image = plt.imshow(data, aspect='auto')
    cbar = plt.colorbar(image, format=ticker.FuncFormatter(fmt))
    cbar.set_label('Intensity in Watt')
    plt.xlabel('y ${\mu}m$')
    plt.ylabel('z ${\mu}m$')

    fig.savefig(name)
    # get the relative path so it works on all operating systems
    rel_path = os.path.realpath('..')
    folder_path = os.path.join(rel_path, "data_visualisation", "DataPlot", "2D")
    # move the file to the correct folder
    shutil.move(name, folder_path)
    plt.show()


def plot2D_line(values, step_time, fiber, name=None):
    """"plots and array of data on a 2d image with a colourwheel"""
    if name is None:
        name = reformattime()

    # setup the settings for the plot
    fig = plt.figure()
    x, y = values
    plt.plot(x, y, linewidth=3)


    plt.title('Simplex line of highest points intensity (W) step time: ' + str(step_time) + "s" + " fiber" + str(fiber))
    plt.xlabel('y ${\mu}m$')
    plt.ylabel('z ${\mu}m$')

    fig.savefig(name)
    # get the relative path so it works on all operating systems
    rel_path = os.path.realpath('..')
    folder_path = os.path.join(rel_path, "data_visualisation", "DataPlot", "simplex_2d_line")
    # move the file to the correct folder
    shutil.move(name, folder_path)
    plt.show()


def plot3D(data, step_time, fiber, name=None):
    """"plots a 3d represtation of scan with coulourbar"""
    if name is None:
        name = reformattime()

    size = data.shape
    xsize, ysize = size
    x_line = np.arange(0, xsize)
    y_line = np.arange(0, ysize)

    x_line, y_line = np.meshgrid(x_line, y_line)

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    plt.xlabel('z ${\mu}m$')
    plt.ylabel('y ${\mu}m$')
    ax.set_zlabel('Value result in watt')
    z = np.full((30, 31), -1)
    for x in range(0, xsize):

        for y in range(0, ysize):
            z = data
    print(z)
    # Plot the surface.
    surf = ax.plot_surface(x_line, y_line, z, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)
    # customize the colourbar
    cbar = plt.colorbar(surf, format=ticker.FuncFormatter(fmt))
    cbar.set_label('Intensity in Watt')
    plt.title('Grid scan test intensity (W) step time: ' + str(step_time) + "s" + " fiber" + str(fiber))

    fig.savefig(name)
    # get the relative path so it works on all operating systems
    rel_path = os.path.realpath('..')
    folder_path = os.path.join(rel_path, "data_visualisation", "DataPlot", "3D")
    # move the file to the correct folder
    shutil.move(name, folder_path)
    plt.show()
