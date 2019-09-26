import numpy as np
from util.point_2D import Point2D

class Simplex_2D:

    def __init__(self, interface, refl=1, exp=2, cont=0.5, shrink=0.3, max_iteration=10, dataset=None ):
        """this initilises all global variables and retrieves the first three data points
        to start the alogritm. it will also initialize the connection with the Thorlabs PM100USB and the
        Thorlabs bpc303 150V piezo controller

        Parameters=
        relf = multiplier of reflection point
        exp = multiplier of expansion point
        cont = multiplier of outside/inside contraction point
        shrink = multiplier of the shrink points
        max_iterations = the number of times one stage of the simplex algorithm gets executed"""
        # assign the varibles to class
        self.refl = refl
        self.exp = exp
        self.cont = cont
        self.shrink = shrink
        self.interfaces = interface
        self.values = None
        self.step_time = 0.8
        self.time_begin = None
        self.time_end = None

        # the list of points 0 = worst 1 = middle and 2 = best
        self.points = []

        # values of the specific points
        self.centroid_point = None
        self.inside_cont = None
        self.outside_cont = None
        self.reflection_point = None
        self.expansion_point = None
        # data for the plotting of the scan
        self.iterations = max_iteration
        self.num_measurements = 0
        self.highest_points = list()
        self.time_begin = None
        self.time_end = None

        self.dataset = dataset

    def function(self, location):
        x, y = location
        z = -pow((y - 1), 2) - pow((x - 1), 2) + 5

        return z

    def test_dataset(self, location):
        y, z = location
        y = int(y)
        z = int(z)
        if 0.0 <= y <= 29.0 and 0.0 <= z <= 29.0:
            x = self.dataset[z][y]
            x = abs(x)
            return x
        return 1.5e-20

    def move_location(self, location):
        """"This function move's the piezo actuators to the desired position as indicated by attribute location(tuple)
        and returns the value at that certain spot"""
        y, z = location
        self.num_measurements += 1
        if self.dataset is not None:
            return self.test_dataset(location)
        else:
            y, z = location
            if 0.0 <= y <= 30.0 and 0.0 <= z <= 30.0:
                self.module_z.move_closed(round(z, 2))
                self.module_y.move_closed(round(y, 2))
                time.sleep(0.8)
                self.points_measured += 1
                return self.PM100.read()
            return 1.5e-20

    def centroid(self, nr_points=2, point_1=None, point_2=None):
        """"calculate the centroid of a 2d line (middle point of line)"""
        p1 = np.asarray(self.points[1].get_location())
        p2 = np.asarray(self.points[2].get_location())

        if point_1 is not None:
            p1 = np.asarray(point_1.get_location())
        if point_2 is not None:
            p2 = np.asarray(point_2.get_location())

        location_centroid = tuple(1/nr_points * (p1 + p2))
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

        location_reflect = tuple(location_centroid + self.refl*(location_centroid - location_low_value))

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
        location_worst= np.asarray(self.points[0].get_location())

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
        #print(location_centroid)
        #print(location_centroid - location_low)
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

            for i in range(3-1):
                if sorted_points[i].x_location > sorted_points[i+1].x_location:
                    sorted_points[i], sorted_points[i+1] = sorted_points[i + 1], sorted_points[i]
                    swapped = True

        return sorted_points

    def exit_condition(self):
        sorted_points = self.sort_points_clockwise()

        area = 0
        j = len(sorted_points)-1
        for i in range(0, len(sorted_points)):
            shoelace = (sorted_points[j].x_location + sorted_points[i].x_location) * (sorted_points[j].y_location
                                                                                          - sorted_points[i].y_location)
            area = area + shoelace
            j = i  # j is previous vertex to i
        area = abs(area / 2.0)

        if area < (30*30/850000):
            return True
        else:
            return False

    def _get_first_points(self, first, size=3):
        """"method that add's the starting points to the point list, these points can either be chose at random or
        with specific intervals between each point
        :param first the location of the first measurement point
        :return the point objects added to a list"""
        y, z = first
        if y > 4 and z > 4:
            second_y = y - size
            second_z = z
            third_y = y - size/2
            third_z = z + 2.6
            #third_z = z + math.tan(60) * (size/2)
        else:
            second_y = y + size
            second_z = z
            third_y = y + size / 2
            third_z = z - 2.6
            #third_z = z - math.tan(60) * (size/2)
        self.points.append(Point2D(first, self.move_location(first)))
        self.points.append(Point2D(((second_y, second_z)), self.move_location((second_y, second_z))))
        self.points.append(Point2D(location=(third_y, third_z), value=self.move_location((third_y, third_z))))
        self.points.sort()

    def scan(self, begin_location):
        self.time_begin = time.time()
        # function that returns retrieves the locations and values of the first points
        self._get_first_points(begin_location.get_location())

        for i in range(self.iterations):
            self.points.sort()
            self.highest_points.append(self.points[2])
            #print("biggest: ", self.points[2].x_location, " ", self.points[2].y_location , " ",
                  #self.points[2].point_value)
            #print("middle: ", self.points[1].x_location, " ", self.points[1].y_location, " ",
                  #self.points[1].point_value)
            #print("smallest: ", self.points[0].x_location, " ", self.points[0].y_location, " ",
                  #self.points[0].point_value)

            self.centroid_point = self.centroid()
            self.reflection_point = self.reflect()

            #print(self.reflection_point > self.points[2])
           # print(self.reflection_point > self.points[1])
            #print(self.reflection_point > self.points[0])




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
               # print("out contracting" + str(self.outside_cont.point_value)+ " " + str(self.reflection_point.point_value))
                if self.outside_cont > self.reflection_point:
                    self.points[0] = self.outside_cont
                    continue
                else:

                    #print(str(self.points[2].get_location()) + " " + str(self.outside_cont.get_location()))
                    outside_centroid = self.centroid(point_1=self.points[2], point_2=self.outside_cont)
                    outside_reflect = self.reflect(point_cent=outside_centroid, point_low=self.points[1])
                    self.points[0] = outside_reflect
                    self.points[1] = self.outside_cont
                    continue
            else:
                self.inside_cont = self.inside_contract()
                #print("ins contracting" + str(self.inside_cont.point_value) + " " + str(self.points[0].point_value))
                if self.inside_cont > self.points[0]:
                    self.points[0] = self.inside_cont
                    continue
                else:
                    #print(str(self.points[2].get_location()) + " " + str(self.inside_cont.get_location()))
                    inside_centroid = self.centroid(point_1=self.points[2], point_2=self.inside_cont)
                    inside_reflect = self.reflect(point_cent=inside_centroid, point_low=self.points[1])
                    self.points[0] = inside_reflect
                    self.points[1] = self.inside_cont
                    continue
        self.time_end = time.time()
        print(self.points[2].get_location())
        print(self.points[2].point_value)
        return self.highest_points

    def point_scan(self):
        pass
        points = []
        for y in np.arange(2.5, 32.5, 5):
            for z in np.arange(2.5, 32.5, 5):
                points.append(Point2D((y,z),self.move_location((y,z))))
                if points[len(points)-1].point_value > 0.5*0.04:
                    break
        points.sort()
        return points

    def get_bestpoint(self):
        return self.points[2]

    def get_measurements(self):
        return self.num_measurements

    def get_time(self):
        excecutiontime = self.time_end - self.time_begin
        excecutiontime = excecutiontime / 60
        return str(excecutiontime) + "minutes"

    def get_highest_points(self):
        return self.highest_points
        # print execution time
        """"
        excecutiontime = self.time_end - self.time_begin
        excecutiontime = excecutiontime / 60

        print(str(excecutiontime) + "minutes")
        print("number measurements: ", self.points_measured)

        location_line_x = list()
        location_line_y = list()
        for point in self.highest_points:
            x, y = point.get_location()
            location_line_x.append(x)
            location_line_y.append(y)
            
       return tuple([location_line_x, location_line_y ])
        """

def f(x,y):
    easy = (pow(x, 2) + pow(y, 2))
    z = math.exp(-4 * easy) + (1 / 4) * math.exp(-6 * pow((math.sqrt(easy) - 1.5), 2))
    return z


if __name__ == '__main__':
    x = np.linspace(-15, 15, 300)
    y = np.linspace(-15, 15, 300)
    x, y = np.meshgrid(x, y)
    f2 = np.vectorize(f)
    array = f2(x,y)
    #print(array)
    dataset = read_file()
    dataset = np.negative(dataset)
    #dataset = np.flipud(dataset)
    simplex = Simplex_2D()
    simplex.scan2()
    line = simplex.save_data()
    points = simplex.point_scan()
    plot_simplex(points=points, line=line)



