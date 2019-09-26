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

class predeterment_points:
    def __init__(self, step_time):
        self.interfaces = None
        self.interfaces = interfaces()

        self.step_time = step_time
        self.time_begin = None
        self.time_end = None

        # data for the plotting of the scan
        self.num_measurements = 0
        self.highest_points = list()
        self.time_begin = None
        self.time_end = None

        self.points_measured = []
        self.peak_point = None
        self.dataset = read_file()
        self.dataset = np.negative(self.dataset)

    def function(self, location):
        x, y = location
        z = -pow((y - 1), 2) - pow((x - 1), 2) + 5

        return z

    def test_dataset(self, location):
        y, z = location
        y = int(y)
        z = int(z)
        if 0.0 <= y <= 29.0 and 0.0 <= z <= 29.0:
            x = self.dataset[y][z]
            x = abs(x)
            return x
        return 1.5e-20

    def paper_function(self, location):
        x, y = location
        easy = (pow(x, 2) + pow(y, 2))
        z = math.exp(-4 * easy) + (1 / 4) * math.exp(-6 * pow((math.sqrt(easy) - 1.5), 2))
        print(z)

        return z

    def Rosenbrock_function(self, location):
        x, y = location
        z = -1 * (pow(1 - x, 2) + 100 * pow((y - pow(x, 2)), 2))
        return z

    def move_location(self, location):
        """"This function move's the piezo actuators to the desired position as indicated by attribute location(tuple)
        and returns the value at that certain spot"""
        y, z = location
        self.num_measurements += 1
        if self.interfaces.is_connected("osrom") is False and self.interfaces.is_connected("controller") is False:
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
        for y in np.arange(2.5, 32.5, 5):
            for z in np.arange(2.5, 32.5, 5):
                self.points_measured.append(Point2D((y,z),self.move_location((y,z))))
                if self.points_measured[len(self.points_measured)-1].point_value > 0.5*0.04:
                    break
        self.sort_points()

    def sort_points(self):
        self.points_measured.sort()

    def get_peak_postion(self):
        return self.points_measured[len(self.points_measured)-1].get_location()



if __name__ == '__main__':
    predeterment_points = predeterment_points(0.5)
    predeterment_points.point_scan()
    print(predeterment_points.get_peak_postion())