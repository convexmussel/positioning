import time
import os
import shutil
import time
import numpy
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


class Plot:
    def __init__(self, fiber=None, title=None, custom_file_name=None):
        self.figure = plt.figure
        self.custom_file_name = custom_file_name
        self.title = title
        self.fiber = fiber

        if self.title is None:
            self.title = input("Enter plot title")

    def plot(self, data, points=False):
        if self.custom_file_name is None:
            self.custom_file_name = Plot.reformattime()

        plt.figure(self.title)

        if type(data) is tuple:
            if points is False:
                print("tuple")
                x, y = data
                plt.plot(x, y, linewidth=3, color="cyan")
            else:
                x, y = data
                plt.scatter(x, y,  s=10, edgecolors='none', c='green')
        else:
            image = plt.imshow(data, aspect='auto', extent=[-15, 15, -15, 15])
            cbar = plt.colorbar(image, format=ticker.FuncFormatter(Plot.fmt))
            cbar.set_label('Intensity in Watt')

    def show(self):
        plt.xlabel('y ${\mu}m$')
        plt.ylabel('z ${\mu}m$')
        plt.title(self.title)
        #plt.savefig(self.custom_file_name)
        # get the relative path so it works on all operating systems
        #rel_path = os.path.realpath('..')
       # folder_path = os.path.join(rel_path, "data_visualisation", "DataPlot", "simplex_snake")
        #print(folder_path)
        #move the file to the correct folder
        #shutil.move(self.custom_file_name, folder_path)
        plt.show()

    @staticmethod
    def fmt(x, pos):
        """"make the notation on the colourbar scientific"""
        a, b = '{:.2e}'.format(x).split('e')
        b = int(b)
        return r'${} \times 10^{{{}}}$'.format(a, b)

    @staticmethod
    def reformattime():
        """returns the time in UTC defined as year-month-day-hour:minute:second. Time is the UTC time"""
        return time.strftime("%Y-%m-%d-%H,%M,%S-UTC-Grindscan.png", time.gmtime())

