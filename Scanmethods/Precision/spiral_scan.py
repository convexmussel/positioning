
from piezo.util.project_root import get_project_root
from piezo.util.point_2D import Point2D
from operator import sub
import time, os, math, configparser, random, pandas
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class Spiral_scan:
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
        self.config_filename = 'precision_algorithms.ini'
        self.config_path = os.path.join(rel_path, "config", self.config_filename)


        # load the config file to assign the values to the variables
        self.load_config(file=file)

    def load_config(self, file=None):
        """ This function read a configfile and assigns the values in the configfile to variables

        @:param file the filename is the user wants to load a different configfile
        """
        if self.dataset is not None:
            self.config_filename = file
        # Read the configfile with the assigned name
        self.config.read(self.config_path)

        # Get values from the configfile and assign them to the correct variables
        self.convergence_rate = self.config.getfloat("Spiral_scan", "convergence rate")
        self.num_beginning = self.config.getint("Spiral_scan", "number of beginning points")
        self.start_size = self.config.getint("Spiral_scan", "starting size")
        self.phi = eval(self.config.get("Spiral_scan", "phi"))
        self.same_points = self.config.getint("Spiral_scan", "number same points")
        self.iterations = self.config.getint("Spiral_scan", "max iterations")

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
        # Round the files down as an interger number
        #y = math.floor(y)
        #z = math.floor(z)
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

    def measure_location(self, location):
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

    def calculate_point(self, previous_point, highest_point):
        """
        :param previous_point: The point object that has been measured last_point.
        :param highest_points: The location that the spiral rotates around.
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
        return (Point2D(new_location, self.measure_location(new_location)))

    def measure_first_points(self):
        measured_beginning = []

        # Get the amount of point that is defined in the config file
        for point in range(0, self.num_beginning):
            y = random.randrange(0, 30)
            z = random.randrange(0, 30)
            measured_beginning.append(Point2D((y,z),self.measure_location((y,z))))
        return(max(measured_beginning))


    def spiral_scan(self, start_point=None):
        # Get the first point to be measured and store this point as the first
        # highest point
        if start_point is not None:
            first_point = start_point
        else:
            first_point = self.measure_first_points()
        self.highest_points.append(first_point)

        # get the location of the first highest point and determine the first point (start)
        # of the spiral
        y,z = self.highest_points[-1].get_location()
        previous_point = Point2D((y+self.start_size,z+self.start_size))

        # number of times same point is peak
        same = 0
        # store this point
        self.points.append(previous_point)

        for i in range(0, self.iterations):
            if same > self.same_points:
                print("max same points reached")
                break
            same += 1
            # calulate the new_point
            new_point = self.calculate_point(previous_point, self.highest_points[-1])

            # if the new point's value is higher than the current highest_point
            # add the new point to the list and move the new point so that
            # the spiral move's the same amount as the center
            if(new_point > self.highest_points[-1]):
                difference = tuple(map(sub, new_point.get_location(), self.highest_points[-1].get_location()))
                self.highest_points.append(new_point)

                new_point = Point2D((np.array(new_point.get_location()) + np.array(difference)))
                same = 0
            # make the new point the previous point and store that point in a list
            previous_point = new_point
            self.points.append(previous_point)


    def get_bestpoint(self):
        return self.highest_points[-1]

    def get_highest_points(self):
        return self.highest_points

    def get_points(self):
        return self.points

    def get_num_measurements(self):
        return self.num_measurements

def fmt(x, pos):
    """"make the notation on the colourbar scientific"""
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

if __name__ == '__main__':
    file = pandas.read_excel(r"C:\Users\Jarno\Dropbox\\nano\code\piezo\um from wave guide30readings turnnob-8-3-1,2-minimaal3.xls")
    numpy = file.to_numpy()
    array = numpy[12:,:]
    array = array.astype('float')

    interface = None
    scan = Spiral_scan(interface=interface, dataset=array.astype('float'))
    scan.spiral_scan()
    points = scan.get_points()
    line_y = []
    line_z = []
    
    for point in points:
        y,z = point.get_location()
        line_y.append(y)
        line_z.append(z)

    fig = plt.figure


    #plt.xlabel('y ${\mu}m$')
    #plt.ylabel('z ${\mu}m$')
    #plt.title("Example with spiral scan")
    #image = plt.imshow(array)
    #cbar = plt.colorbar(image, format=ticker.FuncFormatter(fmt))
    #cbar.set_label('Intensity in A')
    plt.plot(line_y,line_z)
    plt.show()
