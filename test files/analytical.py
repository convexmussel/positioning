import numpy as np
import matplotlib
import csv, math, pandas as pd

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

def function(y,z):
    y = y/3
    z = z/3
    value = math.exp(-4*(y*y + z*z)) + 0.25*math.exp(-6*(math.pow((math.pow((y*y + z*z),0.5)-1.5),2)))
    return value
deviation = np.empty((50,6), dtype='float')
y = np.linspace(-15,15,3001)
z = np.linspace(-15,15,3001)
y,z = np.meshgrid(y,z)
interface = None
vector = np.vectorize(function)
data = vector(y,z)
location = []

plt.figure()

plt.jet()
image = plt.imshow(data, extent=(-15,15,-15,15))
# plt.scatter(deviation[:,2],deviation[:,3] )
#cbar = plt.colorbar(image, format=ticker.FuncFormatter(fmt))
plt.xlabel("Y [${\mu}m$]")
plt.ylabel("Z [${\mu}m$]")
plt.title("Analytical function with sidemodes")
#cbar.ax.set_ylabel('Value')
"""
measurements = np.empty((50,4), dtype='int')
for i in range(0,50):

    random = random_predeterment_points(interface,dataset=data)
    precision = Simplex_2D(interface,dataset=data)
    spiral = Spiral_scan(interface, dataset=data)
    pattern = PatternSearch(interface, dataset=data)


    highest_location = random.point_scan()
    precision.scan(highest_location)
    spiral.spiral_scan()
    pattern.pattern_search(highest_location)
    print(precision.get_bestpoint().get_location())
    print(str(precision.get_num_measurements() + random.get_num_measurements()))
    print(spiral.get_bestpoint().get_location())
    deviation[i][0] = abs(precision.get_bestpoint().get_location()[0] - 15)
    deviation[i][1] = abs(precision.get_bestpoint().get_location()[1] - 15)
    deviation[i][2] = abs(spiral.get_bestpoint().get_location()[0] - 15)
    deviation[i][3] = abs(spiral.get_bestpoint().get_location()[1] - 15)
    deviation[i][4] = abs(pattern.get_bestpoint().get_location()[0] - 15)
    deviation[i][5] = abs(pattern.get_bestpoint().get_location()[1] - 15)
    measurements[i][0] = random.get_num_measurements()
    measurements[i][1] = precision.get_num_measurements()
    measurements[i][2] = spiral.get_num_measurements()
    measurements[i][3] = pattern.get_num_measurements()

print(np.mean(deviation, axis=0))
print(np.mean(measurements, axis = 0))
x = []
y = []
for points in location:
    x.append(points.get_location()[0]-15)
    y.append(points.get_location()[1]-15)

plt.show()
"""
