import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import csv, math, pandas as pd

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
vector = np.vectorize(function)
data = vector(y,z)
location = []
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


image = ax.plot_surface(y,z, data, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
# plt.scatter(deviation[:,2],deviation[:,3] )
#cbar = plt.colorbar(image, format=ticker.FuncFormatter(fmt))
plt.xlabel("Y [${\mu}m$]")
plt.ylabel("Z [${\mu}m$]")
ax.set_zlabel('Value [-]')
plt.title("Analytical function with sidemodes")
plt.show()
