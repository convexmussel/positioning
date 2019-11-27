import math
from piezo.algorithms.pso import PSO
from piezo.algorithms import *
from piezo.util.point_3d import Point3D

import numpy as np
class Algorithms:
    def function(self, y, z):
        y = y-15
        z = z-15
        value = math.exp(-4 * (y * y + z * z)) + 0.25 * math.exp(
            -6 * (math.pow((math.pow((y * y + z * z), 0.5) - 1.5), 2)))
        return value

    def __init__(self):
        self.algorithms = dict()

    def add_algorithm(self, dict):
        self.algorithms.update(dict)

    def execute(self, string):
        point = Point3D(np.array([10, 10]), self.function(10,10))
        print(point.location, point.point_value)
        algorithm = self.algorithms[string]
        while algorithm.state is not finished:
            point = algorithm.next_point(point)
            point.point_value = self.function(point.location[0],point.location[1])
            print(point.location, point.point_value)


spiral = PSO()
algorithms = Algorithms()

algorithms.add_algorithm(spiral.get_dictionary())
algorithms.execute('PSO')
