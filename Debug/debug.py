import data_visualisation.plot_data
import numpy
from data_visualisation.plot_data import plot2D_line
from data_visualisation.plot import Plot
from interface.interfaces import interfaces
from interface.apt.apt import APT
import time
while True:
    interface = interfaces()
    interface.move(15, 18)
    print(interface.read())
    time.sleep(3)
