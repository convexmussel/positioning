
import math
import matplotlib
import pandas, time

import numpy as np
from piezo.Scanmethods.FirstLight.random_points import random_predeterment_points
from piezo.Scanmethods.Precision.simplex_2d import Simplex_2D
from piezo.interface.interfaces import interfaces
from piezo.util.point_2D import Point2D
from piezo.util.project_root import get_project_root
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import operator
def gridscan(interface, start_location,i):
    y_begin, z_begin = start_location
    scan_size = 4
    scan_step = 1
    y_index = 0
    z_index = 0
    test = np.full((11, 11), -1.0, dtype=float)
    step_size = 0.2
    for y in np.linspace(-1, 1, 11):
        for z in np.linspace(-1, 1, 11):
            interface.move(y_begin + y, z_begin + z)
            test[z_index][y_index] = interface.read()
            z_index += 1
        y_index += 1
        z_index = 0
    np.savetxt("scan" + str(i) + ".csv", test, delimiter=",")
    result = np.where(test == np.amax(test))
    linspace = np.linspace(-1, 1, 11)
    location = (y_begin + linspace[int(result[1])], z_begin + linspace[int(result[0])])
    return location, test[int(result[0])][int(result[1])]

index = 0
interface = interfaces()
array = np.empty((50,3), dtype='float')


random = random_predeterment_points(interface)
precision = Simplex_2D(interface)

highest_location = random.point_scan()
precision.scan(highest_location)
start_location = precision.get_bestpoint().get_location()

interface.move(start_location[0],start_location[1])
begin_time = time.time()
end_time = time.time()
while True:
    if begin_time - end_time > 1800:
        break
    start_location, value = gridscan(interface, start_location, index)
    print(start_location)
    print(value)
    array[index][0] = start_location[0]
    array[index][1] = start_location[1]
    array[index][2] = value
    index += 1
    end_time = time.time()
    np.savetxt("quantize drift2.csv", array, delimiter=";")
np.savetxt("quantize drift2.csv", array, delimiter=";")
