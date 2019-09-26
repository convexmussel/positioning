import time

from excel import ExcelPrinter

import numpy
from interface.apt import APT
from interface.pps import PPS


class DigiridooScan:

    def __init__(self):
        self.PM100 = None
        self.module_z = None
        self.module_y = None
        self.setup_controllers()

    def setup_controllers(self):
        print("Initializing osrom")
        self.PM100 = PPS()
        print("Waiting 10 seconds for osrom to be available...")
        time.sleep(10)

        print("Initializing controller")
        controller = APT()
        print("controller connected")
        self.module_y = controller.modules["module2"]
        self.module_z = controller.modules["module3"]
        print(controller.modules)
        # TODO: Replace with polling to see if zero'ing is finished on all modules
        # Sleep to make sure zero-ing finished
        print("Waiting 30 seconds for Piezo Zero process to be completed...")
        time.sleep(30)
        print("Initializing finished")

    def y_axis_scan(self, scan_z, scan_range=30, scan_resolution=1):
        """"loop for every pixel and have a variable resolution so that the user can control the accuracy"""
        PM100_values = []
        # move to the correct z coordinate on stage
        self.module_z.move_closed(scan_z)
        # loop true all the coordinates on the y plane
        for x in range(scan_range / scan_resolution + 1):
            # move the module to the correct place
            self.module_y.move_closed(x / scan_resolution)
            # read the intensity at that point
            PM100_value = self.PM100.read()
            # add the value to the list
            PM100_values.append(PM100_value)
        print(PM100_values)
        return PM100_values

    def z_axis_scan(self, scan_y, scan_range=30, scan_resolution=1):
        """"loop for every pixel and have a variable resolution so that the user can control the accuracy"""
        PM100_values = []
        # move to the correct y coordinate on stage
        self.module_y.move_closed(scan_y)
        # loop true all the coordinates on the y plane
        for y in range(scan_range / scan_resolution + 1):
            # move the module to the correct place
            self.module_z.move_closed(y / scan_resolution)
            # read the intensity at that point
            PM100_value = self.PM100.read()
            # add the value to the list
            PM100_values.append(PM100_value)
        print(PM100_values)
        return PM100_values

    @staticmethod
    def find_max_value(results):
        """"function that returns the index of the highest value in list"""
        max_value = max(results)
        for x in range(len(results)):
            if list[results] == max_value:
                return x

    def digiridoo_scan(self, z_start, y_start):
        scan_values = numpy.full((31, 31), -1.0)
        # scan
        z_peak = z_start
        y_peak = y_start
        time_begin = time.time()
        while 1:
            y_value = self.y_axis_scan(z_peak)
            highest_y_coordinate = self.find_max_value(y_value)
            scan_values[z_peak, :] = y_value

            z_value = self.z_axis_scan(highest_y_coordinate)
            highest_z_coordinate = self.find_max_value(z_value)
            scan_values[:, highest_y_coordinate] = z_value
            print("highest y found: ", highest_y_coordinate)
            print("highest z found: ", highest_z_coordinate)
            print("ypeak: ", y_peak)
            print("zpeak: ", z_peak, "\n")
            if highest_y_coordinate == y_peak:
                if highest_z_coordinate == z_peak:
                    z_peak = highest_z_coordinate
                    y_peak = highest_y_coordinate
                    break
            z_peak = highest_z_coordinate
            y_peak = highest_y_coordinate

        time_end = time.time()

        self.module_y.move_closed(y_peak)
        self.module_z.move_closed(z_peak)
        numpy.savetxt("test.csv", scan_values, delimiter=",")

        print(scan_values)
        excel_file = ExcelPrinter(30, 30, 5, 5)
        excel_file.fillresults(scan_values)
        excel_file.end(time_begin, time_end)
