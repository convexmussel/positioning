import numpy as np
import matplotlib, os
import csv, math
import pandas as pd
from piezo.util.project_root import get_project_root
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import PercentFormatter
from piezo.Scanmethods.FirstLight.random_points import random_predeterment_points
from piezo.Scanmethods.Precision.simplex_2d import Simplex_2D
from piezo.Scanmethods.Precision.spiral_scan import Spiral_scan

root = get_project_root()
array_list = []
for dataset in np.linspace(1, 3, num=3):
    for i in np.linspace(0,30,16):
        folder_path = os.path.join(root, "data_visualisation", "ExcelFiles" + "\\" "scan_files" + "\\" +
                               "um from wave guide" + str(int(30- i)) + "readings turnnob-8-3-1,2-minimaal"
                               + str(int(dataset)) + ".xls")
        file = pd.read_excel(folder_path, header=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11], index=False)
        file = file.astype(dtype=np.float)
        numpy = file.to_numpy()
        array_list.append(numpy)
interface = None
list_y = []
list_z=[]
z = np.linspace(0,30,31)
print(z)

for i in range(0, 16):
    result = np.where(array_list[i] == np.amax(array_list[i]))
    list_y.append(array_list[i][result[0]])
    list_z.append(array_list[i][:,result[1]])

    plt.plot(z, array_list[i][result[0]].flatten())
    plt.plot(z, array_list[i][:,result[1]].flatten())
plt.show()

measurements = np.empty((48,3), dtype='int')
success_s = 0
success_spiral = 0
for i in range(0, 48):
    data= array_list[i]
    random = random_predeterment_points(interface,dataset=data)
    precision = Simplex_2D(interface,dataset=data)
    spiral = Spiral_scan(interface, dataset=data)

    spiral.spiral_scan()

    highest_location = random.point_scan()
    precision.scan(highest_location)
    print(np.amax(data))
    print(precision.get_bestpoint().point_value)
    print(spiral.get_bestpoint().point_value)
    if np.amax(data) == precision.get_bestpoint().point_value:
        success_s = success_s +1
    if np.amax(data) == spiral.get_bestpoint().point_value:
        success_spiral = success_spiral +1
    measurements[i][0] = random.get_num_measurements()
    measurements[i][1] = precision.get_num_measurements()
    measurements[i][2] = spiral.get_num_measurements()
print(np.mean(measurements, axis = 0))
print(success_s/48*100)
print(success_spiral/48*100)
