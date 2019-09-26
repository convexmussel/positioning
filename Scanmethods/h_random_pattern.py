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


class h_random_pattern:
    def __init__(self, max_iteration=10):
        self.values = None
        self.time_begin = None
        self.time_end = None

        self.interfaces = None
        #self.interfaces = interfaces()
        # data for the plotting of the scan
        self.iterations = max_iteration
        self.points_measured = 0
        self.time_begin = None
        self.time_end = None
        self.highest_points = []
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

    def point_scan(self):
        pass
        points = []
        for y in np.arange(2.5, 32.5, 5):
            for z in np.arange(2.5, 32.5, 5):
                points.append(Point2D((y, z), self.move_location((y, z))))
                if points[len(points) - 1].point_value > 0.5 * 0.04:
                    break
        points.sort()
        # print(len(points))
        return points

    def pattern_search(self, point_highest):
        stepsize = 3.0
        shrink = 0.5
        same= 0
        points = []
        self.highest_points = []
        self.highest_points.append(point_highest)
        prev_highest = None
        highest_y, highest_z = point_highest.get_location()
        while True:
            for y in np.linspace(-1, 1, 2):
                points.append(Point2D((highest_y+(stepsize*y), highest_z),
                                      self.move_location((highest_y+(stepsize*y), highest_z))))
            for z in np.linspace(-1, 1, 2):
                points.append(Point2D((highest_y, highest_z+(stepsize*z)),
                                    self.move_location((highest_y, highest_z+(stepsize*z)))))
            points.sort()
            if self.highest_points[len(self.highest_points)-1] < points[len(points)-1]:
                self.highest_points.append(points[len(points)-1])
                highest_y, highest_z = self.highest_points[len(self.highest_points)-1].get_location()
                same = 0
            else:
                stepsize -= shrink
            if self.highest_points[len(self.highest_points)-1] == points[len(points)-1]:
                same += 1
                if same == 4:
                    break

        return self.highest_points
    def get_peak(self):
        return self.highest_points[len(self.highest_points)-1]

    def scan(self):
        points = self.point_scan()
        highest_points = self.pattern_search(points[len(points)-1])
        #print(highest_points[len(highest_points)-1].point_value)
        location_line_x = list()
        location_line_y = list()
        for point in highest_points:
            x, y = point.get_location()
            location_line_x.append(x)
            location_line_y.append(y)
        #print(location_line_x)
       # print(location_line_y)
        return tuple([location_line_x, location_line_y ])

if __name__ == '__main__':
    scan = h_random_pattern()
    scan.scan()
    print(scan.get_peak().get_location())
    print(scan.points_measured)

    plot_simplex(line=scan.scan(), points=scan.point_scan())
