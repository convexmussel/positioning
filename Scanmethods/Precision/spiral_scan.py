import numpy as np
import random
from util.point_2D import Point2D
from interface.apt.apt import APT
from interface.pps.pps import PPS
import time
import math
from data_visualisation.plot_data import plot2D_line
# from interface.interfaces import interfaces
from util.read_excel_file import read_file
from data_visualisation.manual_plot import plot_simplex

from scipy import optimize



class Spiral_scan:
    def __init__(self, max_iteration=50):
        self.values = None
        self.time_begin = None
        self.time_end = None

        # data for the plotting of the scan
        self.iterations = max_iteration
        self.points_measured = 0
        self.highest_points = list()
        self.time_begin = None
        self.time_end = None

        self.dataset = read_file()
        self.dataset = np.negative(self.dataset)

        self.x_points = []
        self.y_points = []

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
        print("measuring:" + str(y) + " " + str(z))
        if self.interfaces is None:
            self.points_measured += 1
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

    def spiral_scan(self):

        pass
        radius = 1
        rangeX = (0, 30)
        rangeY = (0, 30)
        qty = 5  # or however many points you want


        randPoints = []
        excluded = set()
        i = 0
        while i < qty:
            x = random.randrange(*rangeX)
            y = random.randrange(*rangeY)
            if (x, y) in excluded: continue
            self.x_points.append(x)
            self.y_points.append(y)
            randPoints.append((x, y))
            i += 1
        print(randPoints)

        for i in range(0, self.iterations):
            pass

if __name__ == '__main__':
    scan = Spiral_scan()
    scan.spiral_scan()

