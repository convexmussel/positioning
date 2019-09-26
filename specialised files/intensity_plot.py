from data_visualisation.plot import Plot
from util.project_root import get_project_root
import pandas
import numpy as np
import os
from matplotlib.ticker import FuncFormatter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def get_peak(array):
    #print(np.amax(array))
    result = np.where(array == np.amax(array))
    x, y = result
    x = int(x)
    y = int(y)
    return(array[x][y])


def fmt(x, pos):
    """"make the notation on the colourbar scientific"""
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)


def convert_procent(list_values,highest):
    index = 0
    procentage_list = []
    for values in list_values:
        procentage_list.append(values/(highest/100))
    return procentage_list


class plot:
    def __init__(self):
        self.figure, self.ax = plt.subplots()
        self.ax.set_title("Coupling efficiency between waveguide en fiberarray")
        self.ax.set_xlim(30, 0)
        self.ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        self.ax.set_xlabel('Piezo extension (μm)')
        self.ax.set_ylabel('Coupling efficiency')

    def plot(self, data):
        x, y = data
        plt.scatter(x, y, s=10)

    def show(self):
        plt.gca().legend(('dataset 1', 'dataset 2', 'dataset 3', 'summation of all datasets'))
        plt.show()

    def save(self, name):
        plt.savefig(name)

def read_values(dataset=None):
    root = get_project_root()
    list_values = []
    list_distance = []
    for i in range(0,16):
        if dataset is None:
            dataset = ''
        folder_path = os.path.join(root, "data_visualisation", "ExcelFiles" + "\\" "scan_files" + "\\" +
                                   "um from wave guide" + str(30 - i*2) +"readings turnnob-8-3-1,2-minimaal"
                                   + str(dataset) + ".xls")
        file = pandas.read_excel(folder_path)
        numpy = file.to_numpy()
        array = numpy[12:,:]
        array = array.astype('float')
        list_values.append(get_peak(array))
        list_distance.append(30-i*2)
    return  list_values

plot = plot()
arraylist = []
array1 = read_values()
array2 = read_values(2)
array3 = read_values(3)

arraylist.append(array1)
arraylist.append(array2)
arraylist.append(array3)
arraylist.sort()

array = np.add(array1, array2)
normalised = np.add(array, array3)
normalised = normalised/3

linedistance = np.linspace(30, 0, 16)

plot.plot((linedistance,(convert_procent(arraylist[2], arraylist[2][0]))))
plot.plot((linedistance,(convert_procent(arraylist[1], arraylist[2][0]))))
plot.plot((linedistance,(convert_procent(arraylist[0], arraylist[2][0]))))
plot.plot((linedistance,(convert_procent(normalised, arraylist[2][0]))))

plot.show()
