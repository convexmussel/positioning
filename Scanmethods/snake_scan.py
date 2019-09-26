import time

import data_visualisation.plot_data
import numpy

from data_visualisation.excel_store import ExcelPrinter

from interface.interfaces import interfaces


class SnakeScan:

    def  __init__(self, stepsize_z=1, stepsize_y=1):
        self.values = None
        self.step_time = 0.5
        self.time_begin = None
        self.time_end = None
        self.step_size_z = stepsize_z
        self.step_size_y = stepsize_y

        self.interfaces = interfaces()

    def snake_scan(self):
        self.values = numpy.full((31, 31), -1.0)
        self.time_begin = time.time()
        for z in range(31):
            # Move z to desired location
            if z % 2 == 0:
                for y in range(31):
                    # Move X to desired location
                    y_step = y*self.step_size_y
                    self.interfaces.move(y_step, z)
                    sensor_value = self.interfaces.read()
                    print(sensor_value)
                    self.values[z][y] = sensor_value
            else:
                for y in range(31):
                    # Move X to desired location
                    y_step = y * self.step_size_y
                    self.interfaces.move(30 - y_step, z)
                    sensor_value = self.interfaces.read()
                    print(sensor_value)
                    self.values[z][30-y_step] = sensor_value

        self.time_end = time.time()
        self.interfaces
        return self.values

    def save_data(self, remarks):
        # store the data
        excel = ExcelPrinter(1, 1)
        excel.end(self.time_begin, self.time_end, self.values, remarks)

        # get the peak positions
        result = numpy.where(self.values == numpy.amax(self.values))
        # move to peak positions
        print("result x: ", result[0], " result y: ", result[1])
        # self.module_y.move(result[1])
        # self.module_z.move(result[0])

        #data_visualisation.plot_data.plot2D(self.values, self.step_time, 3)
        # data_visualisation.plot_data.plot3D(self.values, self.step_time, 11)

