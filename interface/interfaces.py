from interface.connect_interfaces import connect_interfaces

import time


class interfaces:
    def __init__(self):
        self.module_y = None
        self.module_z = None
        self.module_x = None
        self.interfaces = connect_interfaces()
        self.controller_bay()

    def is_connected(self, device):
        return self.interfaces.is_connected(device)

    def disconnect(self):
        if self.interfaces.controller is not None:
            self.interfaces.controller.disconnect()
        if self.interfaces.osrom is not None:
            self.interfaces.osrom.disconnect()

    def controller_bay(self):
        # check is the controller is connected
        print(self.interfaces.controller)
        if self.interfaces.controller is not None:
            # get control of the correct bays
            self.module_x = self.interfaces.controller.modules["module1"]
            self.module_y = self.interfaces.controller.modules["module2"]
            self.module_z = self.interfaces.controller.modules["module3"]

    def move(self, y, z, x=None):
        # check if the module is connected
        if self.module_y is not None and self.module_z is not None:
            # move the modules to the correct spot
            self.module_y.move(y)
            self.module_z.move(z)
            if x is not None:
                self.module_x.move(x)
            # wait a certain time before moving on to ensure the piezo are done moving
            time.sleep(float(self.interfaces.controller_time))

    def read(self):
        # check if the sensor is connected
        if self.interfaces.osrom is not None:
            # check if the osrom is allowed to read set in config
            if self.interfaces.osrom_reading:
                return self.interfaces.osrom.get_measurement()
        # check if the sensor is connected
        if self.interfaces.PM100 is not None:
            # check if the sensor is allowed to read set in config
            if self.interfaces.PM100_reading:
                return self.interfaces.PM100.read()

    def get_channel(self):
        return self.interfaces.osrom_channel

    def get_fiber(self):
        return self.interfaces.osrom_fiber

    def get_wait_time(self):
        return self.interfaces.controller_time
