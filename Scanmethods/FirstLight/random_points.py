import configparser
import os
import random

import math

import numpy as np
from piezo.util.point_2D import Point2D
from piezo.util.project_root import get_project_root


# noinspection PyAttributeOutsideInit, PyUnusedLocal
class random_predeterment_points:
    def __init__(self, interface, file=None, dataset=None):

        self.interface = interface

        # Definition for variables used for data storage
        self.num_measurements = 0
        self.measured_points = []
        # creation of the configparser object this object is used for the reading of the config file
        self.config = configparser.ConfigParser()

        # Get the relative path of the project, this is needed because the location in the filesystem of the
        # project might change.)
        rel_path = get_project_root()
        self.config_filename = 'first_light.ini'
        self.config_path = os.path.join(rel_path, "config", self.config_filename)


        # store the dataset
        self.dataset = dataset
        # load the config file to assign the values to the variables
        self.load_config(file=file)

    def load_config(self, file=None):
        """ This function read a configfile and assigns the values in the configfile to variables

        @:param file the filename is the user wants to load a different configfile
        """
        if file is not None:
            self.config_filename = file
        # Read the configfile with the assigned name
        self.config.read(self.config_path)

        # Get values from the configfile and assign them to the correct variables
        self.y_range = self.config.getfloat("Random Predetermined points", "Range y")
        self.z_range = self.config.getfloat("Random Predetermined points", "Range z")

        self.Threshold_percentage = self.config.get("Random Predetermined points", "Threshold percentage")
        self.size_y = self.config.getint("Random Predetermined points", "waveguide size y")
        self.size_z = self.config.getint("Random Predetermined points", "waveguide size z")

        self.num_points_x = self.config.getint("Random Predetermined points", "number points x")
        self.num_points_y = self.config.getint("Random Predetermined points", "number points y")
        self.num_points_z = self.config.getint("Random Predetermined points", "number points z")

        if self.Threshold_percentage != 'none':
            self.Threshold_percentage = float(self.Threshold_percentage)

    def test_dataset(self, location):
        """
        :param location: A tuple containing Y, Z coordinates.
        :return: the value of the location measured or if out of bounds of array a bad value
        """
        # Unpack the location tuple into the coordinates
        y, z = location

        y =3001 /30*y
        z = 3001/30*z
        # Round the files down as an interger number
        y = int(round(y))
        z = int(round(z))
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
            if 0.0 <= y <= self.y_range and 0.0 <= z <= self.y_range:
                # Move to the location that the algorithm wants to measure
                self.interface.move(y, z)
                # Increment the amount of measurements done so it is possible to measure the performance
                self.num_measurements += 1
                return self.interface.read()
            return 1.5e-20

    def check_value(self, point):
        """
        Function to check if the value measured at the new location is higher
        than te mean of the previous values
        :param value: The new point_2D object with value
        :return: bool
        """
        mean = 0
        for points in self.measured_points:
            mean += points.point_value
        mean = mean/len(self.measured_points)
        print(mean)
        print(mean+self.Threshold_percentage*mean)
        print(point.point_value)
        if point.point_value >= (mean+self.Threshold_percentage*mean):
            return True
        return False

    def point_scan(self):
        location = []
        # The following loops create the grid that the points are placed in, it calculates the points so that a gradient
        # of the peak is always measured. It does that by making the gaps in the grid a bit smaller than the peak size.
        for y in np.arange(self.size_y / 2, self.y_range + (self.size_y / 2), self.size_y):
            for z in np.arange(self.size_z / 2, self.z_range + (self.size_z / 2), self.size_z):
                location.append((y, z))
        self.num_measurements = 0
        previus_nums = []
        points_measured = 0
        while True:
            while True:
                # Generate random points
                numy = random.randrange(0, self.num_points_y)
                numz = random.randrange(0, self.num_points_z)

                # Check if the point is not already measured
                if [numy, numz] in previus_nums:
                    pass
                else:
                    previus_nums.append([numy, numz])
                    previus_nums.sort()
                    break

            point = Point2D(location[numy * 6 + numz], self.move_location(location[numy * 6 + numz]))
            self.measured_points.append(point)
            points_measured += 1

            print(len(self.measured_points))
            # is the threshold is not set aka none
            if self.Threshold_percentage != "none":
                if self.check_value(point):
                    return self.measured_points[-1]
                # If all the points are measured and the threshold is not reached or the threshold is not set sort the list
                # of points and return the point with the highest value

            if len(self.measured_points) == (self.num_points_y * self.num_points_z):
                self.measured_points.sort()
                print("to many")
                return self.measured_points[-1]

    def sort_points(self):
        self.points_measured.sort()

    def get_peak_position(self):
        return self.points_measured[len(self.points_measured) - 1].get_location()

    def get_measured_points(self):
        return self.measured_points

    def get_num_measurements(self):
        return self.num_measurements
