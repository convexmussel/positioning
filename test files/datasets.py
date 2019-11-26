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
from piezo.Scanmethods.Precision.pattern_scan import PatternSearch

def fmt(x, pos):
    """"make the notation on the colourbar scientific"""
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

def get_peak(array):
    #print(np.amax(array))
    result = np.where(array == np.amax(array))
    x, y = result
    x = int(x)
    y = int(y)
    return x,y

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

measurements = np.empty((48,4), dtype='int')
success_s = 0
success_spiral = 0
success_pattern = 0
deviation = np.empty((48,6), dtype= 'float')
for i in range(0, 48):
    data= array_list[i]
    random = random_predeterment_points(interface,dataset=data)
    precision = Simplex_2D(interface,dataset=data)
    spiral = Spiral_scan(interface, dataset=data)
    pattern = PatternSearch(interface, dataset=data)


    highest_location = random.point_scan()
    precision.scan(highest_location)
    spiral.spiral_scan()
    pattern.pattern_search(highest_location)

    deviation[i][0] = precision.get_bestpoint().get_location()[0]
    deviation[i][1] = precision.get_bestpoint().get_location()[1]
    deviation[i][2] = spiral.get_bestpoint().get_location()[0]
    deviation[i][3] = spiral.get_bestpoint().get_location()[1]
    deviation[i][4] = pattern.get_bestpoint().get_location()[0]
    deviation[i][5] = pattern.get_bestpoint().get_location()[1]
    print(np.amax(data))
    print(precision.get_bestpoint().point_value)
    print(spiral.get_bestpoint().point_value)
    if np.amax(data) == precision.get_bestpoint().point_value:
        success_s = success_s +1
    if np.amax(data) == spiral.get_bestpoint().point_value:
        success_spiral = success_spiral +1
    if np.amax(data) == pattern.get_bestpoint().point_value:
        success_pattern = success_pattern +1

    measurements[i][0] = random.get_num_measurements()
    measurements[i][1] = precision.get_num_measurements()
    measurements[i][2] = spiral.get_num_measurements()
    measurements[i][3] = pattern.get_num_measurements()
deviations_x = 0
deviations_y =  0
deviationz_x = 0
deviationz_y = 0
deviationp_x = 0
deviationp_y = 0
for i in range(0,48):
    x, y = get_peak(array_list[i])
    deviations_x += abs(x-deviation[i][1])
    deviations_y += abs(y-deviation[i][0])
    deviationz_x += abs(x-deviation[i][3])
    deviationz_y += abs(y-deviation[i][2])
    deviationp_x += abs(x-deviation[i][5])
    deviationp_y += abs(y-deviation[i][4])

print(deviations_x/48)
print(deviations_y/48)
print(deviationz_x/48)
print(deviationz_y/48)
print(deviationp_x/48)
print(deviationp_y/48)
print(np.mean(measurements, axis = 0))
print(success_s/48*100)
print(success_spiral/48*100)
print(success_pattern/48*100)

fig = plt.figure()
x = []
y= []
for item in random.measured_points:
    x.append(item.get_location()[0])
    y.append(item.get_location()[1])
plt.scatter(x, y,c= 'magenta')
plt.jet()
image = plt.imshow(data)


cbar = fig.colorbar(image, format=ticker.FuncFormatter(fmt))
cbar.ax.set_ylabel('Photodiode current [A] ')
plt.xlabel('Y ${\mu}m$')
plt.ylabel('Z ${\mu}m$')
plt.title("Showcase of first light algorithm")
plt.show()
