from piezo.algorithms.template import Template
from piezo.util.point_3d import Point3D
import numpy as np
import math, random
from piezo.algorithms import *


class PSO(Template):
    def __init__(self):
        super().__init__()

        self.state = not_started

        self.previous_point = None
        self.to_measure = None
        self.highest_point = None

        self.highest_points = []

        self.no_improvement = 0

    def termination(self):
        if self.num_measurements >= self.iterations:
            return True

        if self.no_improvement > self.same_point:
            return True
        return False

    def check_improved(self, point):
        if self.highest_points[-1].point_value <= point.point_value:
            self.highest_points.append(point)
            self.no_improvement = 0
            return True
        self.no_improvement = self.no_improvement + 1
        return False

    def calculate_point(self, previous_point, highest_point):
        """
        :param previous_point: The point object that has been measured last_point.
        :param highest_point: The location that the spiral rotates around.
        :return: point2D object of the calculated point
        """
        # Get the coordiantes of the previous point
        y0, z0 = previous_point.get_location()

        # Get the coordinates of the highest point
        zero_y, zero_z = highest_point.get_location()

        # create the rotaion matrix and a matrix that contains the coordinates of the previous Point
        rotation_matrix = np.array([[math.cos(self.phi), -math.sin(self.phi)],
                                    [math.sin(self.phi), math.cos(self.phi)]])

        # fill the matrix with the location of the previously measured point
        # minus the coordiantes of the highest point
        location_matrix = np.array([[y0-zero_y], [z0-zero_z]])

        # calulate the coordiantes of the next point by turning the previous coordiantes
        # by the amount of radians defined in phi
        new_location =rotation_matrix.dot(location_matrix) * self.convergence_rate

        # Flatten the array
        new_location = new_location.ravel()

        # change the values in the array
        new_location[0] = new_location[0] + zero_y
        new_location[1] = new_location[1] + zero_z

        # return the multiplication of the matrixes
        self.to_measure = Point3D(new_location)

    def start(self, point):
        # Get the first point to be measured and store this point as the first
        # highest point
        if point is not None:
            first_point = point
        # TODO add condition for no given starting point in start
        self.highest_points.append(first_point)

        # get the location of the first highest point and determine the first point (start)
        # of the spiral
        y, z = self.highest_points[-1].get_location()
        self.to_measure = Point3D((y + self.start_size, z + self.start_size))
        self.state = started

    def next_point(self, point):

        if self.state == started:
            if point is None:
                raise Exception("Point is not allowed to be None")

            self.check_improved(point)
            if self.termination():
                self.state = finished
                return finished

            self.previous_point = point
            self.calculate_point(self.previous_point, self.highest_points[-1])

        if self.state == not_started:
            self.start(point)
        self.num_measurements = self.num_measurements + 1
        return self.to_measure

    def get_dictionary(self):
        return {'PSO': self}

pso = PSO()


# test = dict()
# template = pso.get_dictionary()
# test.update(template)
# test.update({'test' : 12})

