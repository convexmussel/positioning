import configparser
import pandas as pd
import numpy as np
import os
import math
import time
import copy
import scipy as sp
import pydoc

from piezo.util.project_root import get_project_root
from piezo.util.vertex import vertex
from piezo.util.point_3d import Point3D
import itertools
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Ellipse, Polygon
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.colors as colors
from matplotlib.animation import FuncAnimation
from matplotlib import animation
plt.style.use('seaborn-pastel')


class Simplex_3D:

    def __init__(self, interface, file=None, dataset=None):
        # The initial definition of the global variable that is used in benchmarking
        self.num_measurements = 0
        self.excecutiontime = None
        self.config = configparser.ConfigParser()

        self.dataset = dataset
        self.interface = interface
        # Get the relative path of the project, this is needed because the location in the filesystem of the
        # project might change.
        rel_path = get_project_root()
        self.config_filename = 'precision_algorithms.ini'
        self.config_path = os.path.join(
            rel_path, "config", self.config_filename)

        # load the config file to assign the values to the variables
        self.load_config(file=file)

        '''
        self.vertex_history = pd.DataFrame(index=None,columns=None)

        location = np.array([1,2])
        test1 = Point3D([1,3])
        test2 = Point3D([-1,2])
        test3 = Point3D([0,3])

        data = pd.Series([test1, test2, test3])

        dt = np.dtype({'names': ('name', 'point'),
                       'formats': ('U10', 'object')})
        array = np.empty(4, dtype=dt)

        vertex1 = vertex(data)
        vertex1.centroid()
        vertex1.reflect()
        vertex1.expansion()
        vertex1.inside_contract()
        vertex1.inside_reflect()
        vertex1.outside_contract()
        vertex1.outside_reflect()
        locations = []
        for item in vertex1.points:
            locations.append(item.location)

        self.vertex_history = self.vertex_history.append(pd.Series(data=locations,
                                    index=vertex1.points.index),ignore_index=True)
        for index in vertex1.points:
            print(index.location)
        '''

    def valid_location(self, point):
        for coordinate in point.location:
            if 0.0 <= coordinate >= self.x_range:
                return False
        return True

    def test_dataset(self, point):
        """
        :param location: A tuple containing Y, Z coordinates.
        :return: the value of the location measured or if out of bounds of array a bad value
        """
        # Unpack the location tuple into the coordinates
        y, z = location

        y = 3001 / 30 * y
        z = 3001 / 30 * z
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

    def move_location(self, point):
        """
        :param location: A tuple containing Y, Z coordinates.
        :return: The value measured at the requested point or a bad value if not within possible measuring range
        """
        # Check if wanting to measure a dataset or measure with the hardware
        if self.dataset is not None:
            return self.test_dataset(location)
        else:

            # Check if the location that the algorithm wants to measure is within the range of
            # the actuators
            if self.interface is not None:
                if self.valid_location(point):
                    # Move to the location that the algorithm wants to measure
                    self.interface.move_list(point.location)
                    # Increment the amount of measurements done so it is possible to measure the performance
                    self.num_measurements += 1
                    point.point_value = self.interface.read()
                    return point
            point.point_value = 1.5e-20
            return point

    def load_config(self, file=None):
        """ This function read a configfile and assigns the values in the configfile to variables

        @:param file the filename is the user wants to load a different configfile
        """
        if file is not None:
            self.config_filename = file
        # Read the configfile with the assigned name
        self.config.read(self.config_path)

        # Get values from the configfile and assign them to the correct variables
        self.iterations = self.config.getint("Simplex", "iterations")
        self.simplex_size = self.config.getfloat("Simplex", "simplex size")
        self.maximum_rotation = eval(
            self.config.get("Simplex", "maximum rotation"))
        self.x_range = self.config.getfloat("Algorithm independent", "Range x")
        self.y_range = self.config.getfloat("Algorithm independent", "Range y")
        self.z_range = self.config.getfloat("Algorithm independent", "Range z")

    def sort_points(self, points):
        points = pd.Series(np.sort(points.to_numpy()))
        points.reset_index()

        return points

    def store_history(self, vertex):
        values = list(x.location for x in vertex.points)

        series = pd.Series(data=values, index=vertex.points.index)
        self.vertex_history = self.vertex_history.append(
            series, ignore_index=True)

        self.vertex_history.fillna('unknown', inplace=True)

# TODO: Add the calculation of change in angles
    def _get_first_points(self, first):
        location = pd.Series([])
# TODO: Needly replace the 'random' values by non hardcoded values
        location_added = [[0, 0, 4], [0, 4, 0], [
            4, 0, 0], [0, 0, -4], [0, -4, 0], [-4, 0, 0]]

        for i in range(0, self.num_dofs):
            if self.num_dofs > 2:
                location[i] = Point3D(first[:3] + location_added[i])
            else:
                location[i] = Point3D(first[:2] + location_added[i][1:])
            location[self.num_dofs] = (first)
        return location

    def scan(self, begin_location):
        self.num_dofs = len(begin_location)

        nums = list(x for x in range(0, self.num_dofs + 1))
        columns = nums + ['centroid', 'reflection',
                          'inside contract', 'inside centroid', 'inside reflection',
                          'outside contract', 'outside centroid', 'outside reflection']
        self.vertex_history = pd.DataFrame(index=None, columns=columns)

        # Save the time the scan began for benchmark purpose
        time_begin = time.time()
        # function that returns retrieves the locations and values of the first points
        locations = self._get_first_points(begin_location)
        self.sort_points(locations)

        for i in range(0, self.iterations):

            locations = self.sort_points(locations)
            vertex_current = vertex(locations, self.interface)


            if vertex_current.reflection() > locations[locations.index[-1]]:
                if vertex_current.expansion() > vertex_current.reflection():
                    locations[0] = vertex_current.expansion()
                else:
                    locations[0] = vertex_current.reflection()

            elif vertex_current.reflection() > locations[1]:
                locations[0] = vertex_current.reflection()

            elif vertex_current.reflection() > locations[0]:
                if vertex_current.outside_contract() > vertex_current.reflection():
                    locations[0] = vertex_current.outside_contract()
                else:
                    locations[0] = vertex_current.outside_reflect()
                    locations[1] = vertex_current.outside_contract()

            elif vertex_current.inside_contract() > locations[0]:
                locations[0] = vertex_current.inside_contract()
            else:
                locations[0] = vertex_current.inside_reflect()
                locations[1] = vertex_current.inside_contract()
            self.store_history(vertex_current)
        time_end = time.time()
        # self.vertex_history.to_csv(r'C:\Users\Jarno\Dropbox\nano\test.csv')

    def plot_history(self):

        fig, ax = plt.subplots(1)
        ax.imshow(self.dataset)
        ax.set_xlim((0, 30))
        ax.set_ylim((0, 30))

        def init_collection_2D():
            collection = []
            for frame, row in self.vertex_history.iterrows():

                nums = list(x for x in range(0, self.num_dofs + 1))
                array = list(row[x] for x in nums)
                collection.append(Polygon(array))
            return collection

        def init_collection_3D():
            collection = []
            for frame, row in self.vertex_history.iterrows():
                nums = list(x for x in range(0, self.num_dofs + 1))
                array = list(itertools.chain.from_iterable(
                    itertools.combinations(row[nums], 2)))

                array = np.fliplr(np.rot90(array, 3))

                verts = [list(zip(*array))]

                tri = Poly3DCollection(verts)
                tri.set_color(colors.rgb2hex(sp.rand(3)))
                tri.set_edgecolor('k')
                collection.append(tri)
            return collection,

        def animate(i):
            [p.remove() for p in reversed(ax.patches)]
            ax.add_patch(f[i])

        if self.num_dofs == 2:
            f = init_collection_2D()
        else:
            f = init_collection_3D()
        anim = FuncAnimation(fig, animate,
                             frames=20, interval=1000, blit=False)
        ax.imshow(self.dataset)
        mywriter = animation.FFMpegWriter(fps=2)
        anim.save('simplex2d.gif', writer='imagemagick', fps=3)
        plt.show()

data = r'C:\Users\Jarno\Dropbox\nano\code\piezo\data_visualisation\ExcelFiles\scan_files\um from wave guide0readings turnnob-8-3-1,2-minimaal1.xls'
file = pd.read_excel(data)
numpy = file.to_numpy()
array = numpy[12:,:]
array = array.astype(float)
begin = Point3D(np.array([1,2,3,]))
simplex = Simplex_3D(None)
simplex.scan(begin)
simplex.plot_history()
