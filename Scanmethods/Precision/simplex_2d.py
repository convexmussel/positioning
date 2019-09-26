import configparser
import os
import time

import math

import numpy as np
from util.point_2D import Point2D
from util.project_root import get_project_root


# noinspection PyAttributeOutsideInit, PyUnusedLocal
class Simplex_2D:

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
        self.points = []
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

    def centroid(self, nr_points=2, point_1=None, point_2=None):
        """"calculate the centroid of a 2d line (middle point of line)"""
        p1 = np.asarray(self.points[1].get_location())
        p2 = np.asarray(self.points[2].get_location())

        if point_1 is not None:
            p1 = np.asarray(point_1.get_location())
        if point_2 is not None:
            p2 = np.asarray(point_2.get_location())

        location_centroid = tuple(1 / nr_points * (p1 + p2))
        return location_centroid

    def reflect(self, nr_points=2, point_cent=None, point_low=None):
        """"calculates the reflection point f(x) = x_cent + alpha * (x_centroid - point with lowest value) x = point coordinates
            Parameters: number of dimensions
            Returns: point object, with value"""
        location_centroid = np.asarray(self.centroid_point)
        location_low_value = np.asarray(self.points[0].get_location())

        if point_cent is not None:
            location_centroid = np.asarray(point_cent)
        if point_low is not None:
            location_low_value = np.asarray(point_low.get_location())

        location_reflect = tuple(location_centroid + self.refl * (location_centroid - location_low_value))

        # create a point object
        point = Point2D(location_reflect, self.move_location(location_reflect))
        return point

    def expend(self, nr_points=2, point_cent=None, point_relect=None):
        """"calculates the expansion point f(x) = x_cent + beta * (x_reflect - x_centroid) x = point coordinates
            Parameters: number of dimensions
            Returns: point object, with value"""

        location_centroid = np.asarray(self.centroid_point)
        location_reflect = np.asarray(self.reflection_point.get_location())

        if point_cent is not None:
            location_centroid = np.asarray(point_cent)
        if point_relect is not None:
            location_reflect = np.asarray(point_relect.get_location())

        location_expend = tuple(location_centroid + self.exp * (location_reflect - location_centroid))

        # create a point object
        point = Point2D(location_expend, self.move_location(location_expend))
        return point

    def outside_contract(self, nr_points=2):
        """"calculates the outside contract point f(x) = x_cent + gamma * (x_reflect - x_centroid) x = point coordinates
        :param nr_points number of dimensions
        :return point object, with value
        """
        location_centroid = np.asarray(self.centroid_point)
        location_worst = np.asarray(self.points[0].get_location())

        location_outside = tuple(location_centroid + self.cont * (location_centroid - location_worst))

        point = Point2D(location_outside, self.move_location(location_outside))
        return point

    def inside_contract(self, nr_points=2):
        """"calculates the expansion point f(x) = x_cent + gamma * (x_reflect - x_centroid) x = point coordinates
                Parameters: number of dimensions
                    Returns: point object, with value"""
        location_centroid = np.asarray(self.centroid_point)
        location_low = np.asarray(self.points[0].get_location())

        location_inside = tuple(location_centroid - self.cont * (location_centroid - location_low))

        point = Point2D(location_inside, self.move_location(location_inside))
        return point

    def shrink_simplex(self, nr_points=2):
        """"calculates the shrink points replaces all points exept the largest point
        f(x) = x_higest + sigma * (x point to replace - x_highest point) x = point coordinates
        Parameters: number of dimensions
        Returns: list with two point objects, with value"""
        i = 1
        list = []
        while i <= nr_points:
            location_highest = np.asarray(self.points[2].get_location())
            location_point_i = np.asarray(self.points[i - 1].get_location())
            location_i = location_highest + self.shrink * (location_point_i - location_highest)
            i = i + 1
            point = Point2D(location_i, self.move_location(location_i))
            list.append(point)
        return list

    def sort_points_clockwise(self):
        sorted_points = self.points
        swapped = True
        while swapped:
            swapped = False

            for i in range(3 - 1):
                if sorted_points[i].x_location > sorted_points[i + 1].x_location:
                    sorted_points[i], sorted_points[i + 1] = sorted_points[i + 1], sorted_points[i]
                    swapped = True

        return sorted_points

    def exit_condition(self):
        sorted_points = self.sort_points_clockwise()

        area = 0
        j = len(sorted_points) - 1
        for i in range(0, len(sorted_points)):
            shoelace = (sorted_points[j].x_location + sorted_points[i].x_location) * (sorted_points[j].y_location
                                                                                      - sorted_points[i].y_location)
            area = area + shoelace
            j = i  # j is previous vertex to i
        area = abs(area / 2.0)

        if area < (30 * 30 / 850000):
            return True
        else:
            return False

    def _get_first_points(self, first):
        """"method that add's the starting points to the point list, these points can either be chose at random or
        with specific intervals between each point
        :param first the location of the first measurement point
        :return the point objects added to a list"""
        # Unpack the tuple containing location of the first point
        y, z = first
        # Check if the location is greater than the size of the ribs of the simplex
        if y > self.simplex_size and z > self.simplex_size:
            # calculate the location of the second verticle of the simplex
            second_y = y - self.simplex_size
            second_z = z

            # calculate the location of the third verticle of the simplex
            third_y = y - self.simplex_size / 2
            third_z = z - math.tan(math.radians(60)) * (self.simplex_size / 2)
        else:
            # calculate the location of the second verticle of the simplex
            second_y = y + self.simplex_size
            second_z = z

            # calculate the location of the third verticle of the simplex
            third_y = y + self.simplex_size / 2
            third_z = z + math.tan(math.radians(60)) * (self.simplex_size / 2)

        # Fill the initial points with values
        self.points.append(Point2D(first, self.move_location(first)))
        self.points.append(Point2D(location=(second_y, second_z), value=self.move_location((second_y, second_z))))
        self.points.append(Point2D(location=(third_y, third_z), value=self.move_location((third_y, third_z))))
        self.points.sort()

    def scan(self, begin_location):
        # Save the time the scan began for benchmark purpose
        self.time_begin = time.time()
        # function that returns retrieves the locations and values of the first points
        self._get_first_points(begin_location.get_location())

        for i in range(self.iterations):
            # ensure that the points are in the correct order index 0 point with smallest value en n with the highest
            # value
            self.points.sort()

            # Save the highest point
            self.highest_points.append(self.points[2])

            # Calculate the centroid and reflect point
            self.centroid_point = self.centroid()
            self.reflection_point = self.reflect()

            # Check paper about nelder mead algorithm for explanation.
            if self.reflection_point > self.points[2]:
                self.expansion_point = self.expend()
                if self.expansion_point > self.reflection_point:
                    self.points[0] = self.expansion_point
                    continue
                else:
                    self.points[0] = self.reflection_point
                    continue
            elif self.reflection_point > self.points[1]:
                self.points[0] = self.reflection_point
                continue
            elif self.reflection_point > self.points[0]:
                self.outside_cont = self.outside_contract()
                if self.outside_cont > self.reflection_point:
                    self.points[0] = self.outside_cont
                    continue
                else:
                    outside_centroid = self.centroid(point_1=self.points[2], point_2=self.outside_cont)
                    outside_reflect = self.reflect(point_cent=outside_centroid, point_low=self.points[1])
                    self.points[0] = outside_reflect
                    self.points[1] = self.outside_cont
                    continue
            else:
                self.inside_cont = self.inside_contract()
                if self.inside_cont > self.points[0]:
                    self.points[0] = self.inside_cont
                    continue
                else:
                    inside_centroid = self.centroid(point_1=self.points[2], point_2=self.inside_cont)
                    inside_reflect = self.reflect(point_cent=inside_centroid, point_low=self.points[1])
                    self.points[0] = inside_reflect
                    self.points[1] = self.inside_cont
                    continue
        self.time_end = time.time()
        return self.highest_points

    def get_bestpoint(self):
        return self.points[2]

    def get_num_measurements(self):
        return self.num_measurements

    def get_exc_time(self):
        excecutiontime = self.time_end - self.time_begin
        return excecutiontime

    def get_highest_points(self):
        return self.highest_points
