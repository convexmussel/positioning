import configparser
import os
import random

import math

import numpy as np
from util.point_2D import Point2D
from util.project_root import get_project_root


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
        self.config_path = os.path.join(rel_path, "config")
        self.config_filename = 'first_light.ini'

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
        self.config.read(self.config_path + "\\" + self.config_filename)

        # Get values from the configfile and assign them to the correct variables
        self.y_range = self.config.getfloat("Random Predetermined points", "Range y")
        self.z_range = self.config.getfloat("Random Predetermined points", "Range z")

        self.threshold = self.config.get("Random Predetermined points", "Threshold value")
        self.size_y = self.config.getint("Random Predetermined points", "waveguide size y")
        self.size_z = self.config.getint("Random Predetermined points", "waveguide size z")

        self.num_points_x = self.config.getint("Random Predetermined points", "number points x")
        self.num_points_y = self.config.getint("Random Predetermined points", "number points y")
        self.num_points_z = self.config.getint("Random Predetermined points", "number points z")

        if self.threshold != 'none':
            self.threshold = float(self.threshold)

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
            if 0.0 <= y <= self.y_range and 0.0 <= z <= self.y_range:
                # Move to the location that the algorithm wants to measure
                self.interface.move(y, z)
                # Increment the amount of measurements done so it is possible to measure the performance
                self.num_measurements += 1
                return self.interface.read()
            return 1.5e-20

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
                    print([numy, numz])
                    break

            print(str(numy + numz * 6) + ' ' + str(location[numy * 6 + numz]))
            point = Point2D(location[numy * 6 + numz], self.move_location(location[numy * 6 + numz]))
            self.measured_points.append(point)
            points_measured += 1
            print(points_measured)
            # is the threshold is not set aka none
            if self.threshold != "none":
                if point.point_value > self.threshold:
                    return self.measured_points[-1]
                # If all the points are measured and the threshold is not reached or the threshold is not set sort the list
                # of points and return the point with the highest value
            elif len(self.measured_points) == self.num_points_y * self.num_points_z:
                self.measured_points.sort()
                return self.measured_points[-1]

    def sort_points(self):
        self.points_measured.sort()

    def get_peak_position(self):
        return self.points_measured[len(self.points_measured) - 1].get_location()

    def get_measured_points(self):
        return self.measured_points

