import numpy as np
import pandas as pd
import configparser
import os

from piezo.util.project_root import get_project_root
from piezo.util.point_3d import Point3D


def get_sum(array):
    value = np.zeros(array.size)
    for index in array:
        value += index.location
    return value


class vertex:
    def __init__(self, points, interface, file=None, dataset=None):
        # array with the points
        self.points = points

        self.interface = interface
        self.dataset = None
        # number of dimensions
        self.number_dofs = len(self.points[0].location)

        # variable for reflection
        self.alpha = None

        # variable for expansion
        self.beta = None

        # variable for contraction
        self.gamma = None

        # creation of the configparser object this object is used for the reading of the config file
        self.config = configparser.ConfigParser()

        # Get the relative path of the project, this is needed because the location in the filesystem of the
        # project might change.
        rel_path = get_project_root()
        self.config_filename = 'precision_algorithms.ini'
        self.config_path = os.path.join(rel_path, "config", self.config_filename)

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
        self.alpha = self.config.getfloat("Simplex", "reflection")
        self.beta = self.config.getfloat("Simplex", "expansion")
        self.gamma = self.config.getfloat("Simplex", "contraction")
        self.x_range = self.config.getfloat("Algorithm independent", "Range x")
        self.y_range = self.config.getfloat("Algorithm independent", "Range y")
        self.z_range = self.config.getfloat("Algorithm independent", "Range z")

    def centroid_exist(self):
        try:
            if self.points['centroid'] is not None:
                return True
        except KeyError:
            self.centroid()
            return True

    def centroid(self):
        centroid = Point3D(get_sum(self.points[1:]) * (1/self.number_dofs))
        self.points = self.points.append(pd.Series([centroid], index=["centroid"]))
        return centroid

    def reflection(self):
        try:
            if self.points['reflection'] is not None:
                return self.points['reflection']
        except KeyError:
            self.centroid_exist()

            reflection = Point3D(self.points['centroid'] + self.alpha *
                                (self.points['centroid'] - self.points[0]))
            self.points = self.points.append(pd.Series([reflection],
                                                        index=['reflection']))
            return reflection

    def expansion(self):
        try:
            if self.points['expansion'] is not None:
                return self.points['expansion']
        except KeyError:
            self.centroid_exist()
            expansion = Point3D(self.points['centroid'] + self.beta *
                            (self.points['reflection'] - self.points['centroid']))
            self.points = self.points.append(pd.Series([expansion],
                                                        index=["expansion"]))
            return expansion

    def inside_contract(self):
        try:
            if self.points['inside contract'] is not None:
                return self.points['inside contract']
        except KeyError:
            self.centroid_exist()
            inside_contract = Point3D(self.points['centroid'] - self.gamma *
                                    (self.points['centroid'] - self.points[0]))
            self.points = self.points.append(pd.Series([inside_contract],
                                                    index=["inside contract"]))
            return inside_contract

    def inside_reflect(self):
        try:
            if self.points['inside reflection'] is not None:
                return self.points['inside reflection']
        except KeyError:
            inside_contract = pd.Series(self.points['inside contract'])
            points = self.points[2:self.number_dofs+1]
            points = pd.concat([inside_contract, points])

            inside_centroid = Point3D(get_sum(points) * (1/self.number_dofs))
            self.points = self.points.append(pd.Series([inside_centroid], index=['inside centroid']))

            inside_reflection = Point3D(self.points['inside centroid'] + self.alpha *
                                (self.points['inside centroid'] - self.points[self.number_dofs-2]))
            self.points = self.points.append(pd.Series([inside_reflection], index=['inside reflection']))

            return inside_reflection

    def outside_contract(self):
        try:
            if self.points['outside contract'] is not None:
                return self.points['outside contract']
        except KeyError:
            self.centroid_exist()
            outside_contract = Point3D(self.points['centroid'] + self.gamma *
                                    (self.points['centroid'] - self.points[0]))
            self.points = self.points.append(pd.Series([outside_contract],
                                                    index=["outside contract"]))
            return outside_contract

    def outside_reflect(self):
        try:
            if self.points['outside reflection'] is not None:
                return self.points['outside reflection']
        except KeyError:
            outside_contract = pd.Series(self.points['outside contract'])
            points = self.points[2:self.number_dofs+1]
            points = pd.concat([outside_contract, points])

            outside_centroid = Point3D(get_sum(points) * (1/self.number_dofs))
            self.points = self.points.append(pd.Series([outside_centroid], index = ['outside centroid']))

            outside_reflection = Point3D(self.points['outside centroid'] + self.alpha *
                                (self.points['outside centroid'] - self.points[self.number_dofs-2]))
            self.points = self.points.append(pd.Series([outside_reflection], index = ['outside reflection']))

            return outside_reflection
