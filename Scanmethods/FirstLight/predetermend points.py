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
    def __init__(self, interface, file=None, dataset=None ):
        self.interfaces = None
        self.interfaces = interfaces()

        self.time_begin = None
        self.time_end = None

        # data for the plotting of the scan
        self.num_measurements = 0
        self.highest_points = list()

        self.points_measured = []
        self.peak_point = None

    def load_config(self, file=None):
        """ This function read a configfile and assigns the values in the configfile to variables

        @:param file the filename is the user wants to load a different configfile
        """
        if file is not None:
            self.config_filename = file
        # Read the configfile with the assigned name
        self.config.read(self.config_path + "\\" + self.config_filename)

        # Get values from the configfile and assign them to the correct variables
        self.refl = self.config.getfloat("Simplex", "reflection")
        self.exp = self.config.getfloat("Simplex", "expansion")
        self.cont = self.config.getfloat("Simplex", "contraction")
        self.iterations = self.config.getint("Simplex", "iterations")
        self.simplex_size = self.config.getfloat("Simplex", "simplex size")

    def test_dataset(self, location):
        """
        :param location: A tuple containing Y, Z coordinates.
        :return: the value of the location measured or if out of bounds of array a bad value
        """
        # Unpack the location tuple into the coordinates
        y, z = location

        # Round the files down as an interger number
        y = math.floor(y)
        z = math.floor(z)
        # Try to get the value from the dataset the value is out of range catch the exeption
        # and return a value that is always not interesting for the algorithm
        try:
            self.num_measurements += 1
            value = self.dataset[z][y]
            # Make sure that the value is always positive
            value = abs(value)
            return value
        except IndexError:
            return 1.5e-20

    def move_location(self, location):
        """
        :param location: A tuple containing Y, Z coordinates.
        :return: The value measured at the requested point or a bad value if not within possible measuring range
        """
        # Check if wanting to measure a dataset or measure with the hardware
        if self.dataset is not None:
            return self.test_dataset(location)
        else:
            # Unpack the location tuple into the coordinates
            y, z = location
            # Check if the location that the algorithm wants to measure is within the range of
            # the actuators
            if 0.0 <= y <= 30.0 and 0.0 <= z <= 30.0:
                # Move to the location that the algorithm wants to measure
                self.interface.move(y, z)
                # Increment the amount of measurements done so it is possible to measure the performance
                self.num_measurements += 1
                return self.interface.read()
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