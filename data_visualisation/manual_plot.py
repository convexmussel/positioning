
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm
from util.read_excel_file import read_file
import numpy as np
from util.project_root import get_project_root
import os
import shutil
import time
import math
import pandas
def fmt(x, pos):
    """"make the notation on the colourbar scientific"""
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)


def reformattime():
    """returns the time in UTC defined as year-month-day-hour:minute:second. Time is the UTC time"""
    return time.strftime("%Y-%m-%d-%H,%M,%S-UTC-Grindscan.png", time.gmtime())

def plot_simplex(line=None, points=None):

    dataset = read_file()
    dataset = np.negative(dataset)
    #dataset = np.flipud(dataset)

    fig = plt.figure()
    plt.title('simplex plot with prescanned dots')
    image = plt.imshow(dataset, aspect='auto', label='Gridscan of simplex')
    cbar = plt.colorbar(image, format=ticker.FuncFormatter(fmt))
    cbar.set_label('Intensity in mW')
    plt.xlabel('y ${\mu}m$')
    plt.ylabel('z ${\mu}m$')


    if points is not None:
        z_list = []
        y_list = []
        for point in points:
            y, z= point.get_location()
            z_list.append(z)
            y_list.append(y)
        plt.scatter(z_list, y_list, s=10, c='purple', label='predetermed points')

    if line is not None:
        x, y = line

        plt.plot(x, y, linewidth=3, color="cyan", label='pattern scan route line')
        plt.scatter(x[0], y[0], s=15, c='Brown', zorder=10 ,label='First point pattern scan')
    plt.gca().legend(loc='upper right')
    #fig.savefig("simplex with predetermend points")
    plt.show()



def plot2D():
    """"plots and array of data on a 2d image with a colourwheel"""
    root = get_project_root()
    array_list = []
    for dataset in np.linspace(1, 3, num=3):
        for i in np.linspace(2,0, 3):
            if i == 1:
                number = 16
            if i == 2:
                number = 0
            if i == 0:
                number = 30
            folder_path = os.path.join(root, "data_visualisation", "ExcelFiles" + "\\" "scan_files" + "\\" +
                                   "um from wave guide" + str(abs(number)) + "readings turnnob-8-3-1,2-minimaal"
                                   + str(int(dataset)) + ".xls")
            file = pandas.read_excel(folder_path, header=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11], index=False)
            file = file.astype(dtype=np.float)
            numpy = file.to_numpy()
            array_list.append(numpy)

    fig, axs = plt.subplots(1, 3, sharex=True, sharey=True, figsize=(12,3.5))
    fig.suptitle('Plots of dataset 1')
    fig.text(0.43, 0.04, 'Y displacement ${\mu}m$', ha='center')
    fig.text(0.04, 0.5, 'Z displacement ${\mu}m$', va='center', rotation='vertical')
    plotnum = 0
    plt.jet()
    for ax in axs:
        image = ax.imshow(array_list[plotnum])
        ax.invert_yaxis()
        plotnum += 1

    axs[0].set_title('X displacement 0${\mu}m$')
    axs[1].set_title('X displacement 14${\mu}m$')
    axs[2].set_title('X displacement 30${\mu}m$')

    cbar = fig.colorbar(image, ax=axs.ravel().tolist(), format=ticker.FuncFormatter(fmt))
    cbar.ax.set_ylabel('Intensity (mA)')
    plt.show()
def plot3D():
    """"plots a 3d represtation of scan with coulourbar"""
    def f(x,y):
        return math.exp(-4 * (pow(x, 2) + pow(y, 2))) + (1 / 4) * math.exp(-6 * pow((math.sqrt((pow(x, 2) + pow(y, 2))) - 1.5), 2))

    x_line = np.arange(-15, 15, 0.1)
    y_line = np.arange(-15, 15, 0.1)

    x, y = np.meshgrid(x_line, y_line)
    f2 = np.vectorize(f)

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    plt.xlabel('z ${\mu}m$')
    plt.ylabel('y ${\mu}m$')
    ax.set_zlabel('Intensity')
    print(f2(x, y))
    # Plot the surface.
    surf = ax.plot_surface(x, y, f2(x, y), cmap=cm.coolwarm,
                          linewidth=0, antialiased=False)

    plt.show()

if __file__ == "__main__":
    plot2D()