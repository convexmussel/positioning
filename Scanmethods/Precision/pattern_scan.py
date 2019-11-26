import configparser
import os
import time

import math

from piezo.util.point_2D import Point2D
from piezo.util.project_root import get_project_root


# noinspection PyAttributeOutsideInit, PyUnusedLocal
class PatternSearch:
    def __init__(self, interface, file=None, dataset=None):
        """This function calls the function to read the configuration file and assigns the parameters
        to the variables

        @:param interface The abstraction of the communication with the hardware
        @:param file the filename is the user wants to load a different configfile
        @:param dataset A dataset to test the simplex algoritm on.
        """
        # Assign the abstraction of the communication with the hardware to a variable
        self.interface = interface
        # Assign the dataset that the code needs to execute on to a object is the parameter is not given
        # this objects value will be None
        self.dataset = dataset

        # creation of the configparser object this object is used for the reading of the config file
        self.config = configparser.ConfigParser()

        # Definition for variables used for data storage
        self.highest_points = []

        # The initial definition of the global variable that is used in benchmarking
        self.num_measurements = 0

        # Get the relative path of the project, this is needed because the location in the filesystem of the
        # project might change.
        rel_path = get_project_root()
        self.config_path = os.path.join(rel_path, "config")
        self.config_filename = 'precision_algorithms.ini'

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
        self.shrink_factor = self.config.getfloat("Pattern_scan", "shrink factor")
        self.size = self.config.getfloat("Pattern_scan", "initial size")
        self.threshold_samepoints = self.config.getint("Pattern_scan", "number same points")
        self.iterations = self.config.get("Pattern_scan", "number iterations")

        # check if set values are none, if assigned to none give the amount of samepoints the value -1 and
        # the variable iterations True
        if self.threshold_samepoints == "none":
            self.threshold_samepoints = None
        if self.iterations == "none":
            self.iterations = None


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
            if 0.0 <= y <= 30.0 and 0.0 <= z <= 30.0:
                # Move to the location that the algorithm wants to measure
                self.interface.move(y, z)
                # Increment the amount of measurements done so it is possible to measure the performance
                self.num_measurements += 1
                return self.interface.read()
            return 1.5e-20

    def check_same_values(self, num_same_values):
        """
        Fucntion to compare the amount of time the save value has been found

        :param num_same_values:
        :return: True if the the amount of times there isnt a new found point is equal of larger then the
        specified amount
        :return: False if the threshold has not been set, True if the the amount of times there
        isnt a new found point is not equal of larger then the
        specified amount
        """
        if self.threshold_samepoints is None:
            return False
        elif self.threshold_samepoints <= num_same_values:
            return True
        return False

    def measure_points(self, locations):
        """
        Function to measure points at specified locations
        :param locations: the locations in 2d of each point.
        :return: The points that are measured point_2d objects
        """
        measured_points = []
        for location in locations:
            measured_point = Point2D(location, self.move_location(location=location))
            measured_points.append(measured_point)
        return measured_points

    def calculate_point_locations(self):
        """
        :return: Returns a list of location for points to be measured
        """
        point_locations = []
        highest_y, highest_z = self.highest_point.get_location()

        point_locations.append((highest_y + self.shrink_factor, highest_z + self.shrink_factor))
        point_locations.append((highest_y + self.shrink_factor, highest_z - self.shrink_factor))
        point_locations.append((highest_y - self.shrink_factor, highest_z + self.shrink_factor))
        point_locations.append((highest_y - self.shrink_factor, highest_z - self.shrink_factor))

        return point_locations

    def pattern_search(self, point_highest):
        self.time_begin = time.time()
        self.highest_points.append(point_highest)
        self.measured_points = []
        self.highest_point = point_highest
        times_same_value = 0
        while True:
            # get the locations of the points to be measured
            point_locations = self.calculate_point_locations()
            # measure the points at the cacluated positions
            point_values = self.measure_points(point_locations)
            # add the highest point to the list for easy comparison
            point_values.append(self.highest_point)
            # sort the points so the values of the points are in the correct order
            point_values.sort()
            # If the highest point has not changed check the amount of times the highest point has not
            # changed if the highest value has not changed more times than then the specified amount exit
            if point_values[-1] == self.highest_point:
                if self.check_same_values(times_same_value):
                    break
                times_same_value += 1

            # if the last element of the list of measured points is higher than the previus highest point
            # make that point the new point with highest value
            if point_values[-1] > self.highest_point:
                # Make the new found point the highest point
                self.highest_points.append(point_values[-1])
                self.highest_point = point_values[-1]
                times_same_value = 0
            else:
                # Shrink the search radius of the pattern
                self.size -= self.shrink_factor
        self.time_end = time.time()


    def get_bestpoint(self):
        return self.highest_point


    def get_num_measurements(self):
        return self.num_measurements


    def get_exc_time(self):
        return self.time_end - self.time_begin


    def get_highest_points(self):
        return self.highest_points
