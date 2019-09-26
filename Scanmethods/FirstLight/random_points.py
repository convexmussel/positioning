import numpy as np
from util.point_2D import Point2D
from interface.apt.apt import APT
from interface.pps.pps import PPS
import time
import math
from data_visualisation.plot_data import plot2D_line
from interface.interfaces import interfaces
from util.read_excel_file import read_file
from data_visualisation.plot import Plot
from data_visualisation.manual_plot import plot3D
from data_visualisation.manual_plot import plot_simplex
import random

class random_points:
    def __init__(self, interface=None, dataset=None):
        self.interfaces = None
        if interface is not None:
            self.interfaces = interface
        else:
            self.interfaces = interfaces()

        self.time_begin = None
        self.time_end = None

        # data for the plotting of the scan
        self.num_measurements = 0
        self.highest_points = list()
        self.time_begin = None
        self.time_end = None

        self.points_measured = []
        self.peak_point = None

        self.dataset = dataset

    def test_dataset(self, location):
        y, z = location
        y = int(y)
        z = int(z)
        if 0.0 <= y <= 29.0 and 0.0 <= z <= 29.0:
            x = self.dataset[z][y]
            x = abs(x)
            return x
        return 1.5e-20

    def move_location(self, location):
        """"This function move's the piezo actuators to the desired position as indicated by attribute location(tuple)
        and returns the value at that certain spot"""
        y, z = location
        self.num_measurements += 1
        if self.dataset is not None:
            return self.test_dataset(location)
        else:
            y, z = location
            if 0.0 <= y <= 30.0 and 0.0 <= z <= 30.0:
                self.module_z.move_closed(round(z, 2))
                self.module_y.move_closed(round(y, 2))
                time.sleep(0.8)
                self.points_measured += 1
                return self.PM100.read()
            return 1.5e-20

    def point_scan(self):
        array = []
        for y in np.arange(2.5, 32.5, 5):
            for z in np.arange(2.5, 32.5, 5):
                array.append(Point2D((y,z),self.move_location((y,z))))
        self.num_measurements = 0
        previus_nums = []
        while True:
            while True:
                contains = False
                numx = random.randrange(0,6)
                numy = random.randrange(0,6)
                for nums in previus_nums:

                    if [numx, numy] == nums:
                        contains = True
                        break
                if contains is False:
                    previus_nums.append([numx, numy])
                    break
            self.num_measurements += 1
            if array[numx + numy*6].point_value > 0.6 * 0.003:
                return array[numx + numy*6]

    def sort_points(self):
        self.points_measured.sort()

    def get_peak_postion(self):
        return self.points_measured[len(self.points_measured)-1].get_location()

    def get_points(self):
        return self.points_measured

    def get_measurements(self):
        return self.num_measurements

if __name__ == '__main__':

    steps = 0
    for i in range(0, 1000):
        random_points2 = random_points(0.5)
        random_points2.point_scan_test()
        steps += random_points2.get_measurements()
        print(random_points2.get_measurements())
    print(steps / 1000)
