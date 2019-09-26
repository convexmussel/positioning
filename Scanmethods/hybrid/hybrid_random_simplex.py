from Scanmethods.FirstLight.random_points import random_points
from Scanmethods.Precision.simplex_2d import Simplex_2D
from interface.interfaces import interfaces
import pandas
from util.project_root import get_project_root
import os
import numpy as np


def read_values(dataset=None):
    root = get_project_root()
    list_array = []
    for i in range(0, 16):
        if dataset is None:
            dataset = ''
        folder_path = os.path.join(root, "data_visualisation", "ExcelFiles" + "\\" "scan_files" + "\\" +
                                   "um from wave guide" + str(30 - i * 2) + "readings turnnob-8-3-1,2-minimaal"
                                   + str(dataset) + ".xls")
        file = pandas.read_excel(folder_path)
        numpy = file.to_numpy()
        array = numpy[12:, :]
        list_array.append(array.astype('float'))
    return list_array


def get_deviation(found_bestpoints, datasets):
    z_deviation = 0
    y_deviation = 0
    found = 0
    num_iterations = 0
    for points in found_bestpoints:

        result = np.where(datasets[num_iterations] == np.amax(datasets[num_iterations]))
        y = int(result[0])
        z = int(result[1])
        z_found, y_found  = points.get_location()
        if int(z_found) == int(z) and int(y_found) == int(y):
            found += 1
        y_deviation += abs(y_found - y)
        z_deviation += abs(z_found - z)
        num_iterations += 1
    print("y deviation: "+ str(y_deviation/num_iterations))
    print("z deviation: "+ str(z_deviation/num_iterations))
    print(found/num_iterations*100)
    return y_deviation, z_deviation

def find_peak():
    interface = interfaces()
    total_f = 0
    total_p = 0
    best_points = []
    for i in range(0, 16):
        first_light = random_points(interface, dataset=datasets[i])
        good_enough_point = first_light.point_scan()
        precision = Simplex_2D(interface, good_enough_point, dataset=datasets[i])
        precision.scan(good_enough_point)
        best_points.append(precision.get_bestpoint())
        total_f += first_light.num_measurements
        total_p += precision.get_measurements()
    return best_points, total_f, total_p
datasets = read_values(2)
# move to peak positions
total_m = 0
total_f = 0
total_p = 0
deviation_y = 0
deviation_z = 0
for x in range(0, 10):
    best_points, measurements_f, measurements_p = find_peak()
    total_m += measurements_f + measurements_p
    total_p += measurements_p
    total_f += measurements_f
    deviation_y2, deviation_z2 = get_deviation(best_points, datasets)
    deviation_y += deviation_y2
    deviation_z += deviation_z2
print("avarage measurements: " + str(total_m/ (16*10)))
print("avarage deviation y: " + str(deviation_y/160))
print("avarage deviation z: " + str(deviation_z/160))
print("avarage measurements f: " + str(total_f/160))
print("avarage measurements p: " + str(total_p/160))