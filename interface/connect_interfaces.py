from interface.osrom.pyosrom.application import Osrom
from interface.pps.pps import PPS
from pyvisa import errors
from interface.apt.apt import APT
import numpy
import os
import configparser
from util.project_root import get_project_root


class connect_interfaces:
    def __init__(self):
        self.osrom = None
        self.PM100 = None
        self.controller = None

        self.osrom_channel = None
        self.osrom_fiber = None
        self.osrom_reading = None

        self.PM100_reading = None

        self.controller_time = None
        self.controller_closed = None
        rel_path = get_project_root()
        folder_path = os.path.join(rel_path, "interface", "config.ini")
        self.config_filename = folder_path

        self.config = configparser.ConfigParser()
        self.load_config(self.config_filename)
        self.connect_osrom()
        self.connect_pm100()
        self.connect_controller()

    def is_connected(self, device):
        device = device.lower()
        dict = {
            "osrom": self.osrom,
            "pm100": self.PM100,
            "controller": self.controller
        }

        if dict[device] is not None:
            if dict[device].is_connected():
                return True
        return False

    def load_config(self, file=None):
        if file is not None:
            self.config_filename = file

        self.config.read(file)
        print(self.config.sections())
        self.osrom_channel = self.config.get("osrom", "channel")
        self.osrom_fiber = self.config.get("osrom", "fiber")
        self.osrom_reading = self.config.get("osrom", "reading")

        self.PM100_reading = self.config.get("PM100", "reading")

        self.controller_time = self.config.get("piezo controller", "wait time")
        self.controller_closed = self.config.get("piezo controller", "closed loop")

    def connect_osrom(self):
        try:
            self.osrom = Osrom()
            print("Osrom connected")
        except Exception:
            pass

    def connect_pm100(self):
        try:
            self.PM100 = PPS()
            print("PM100 connected")
        except errors.VisaIOError:
            pass

    def connect_controller(self):
        try:
            self.controller = APT(bool(self.controller_closed))
        except IOError:
            pass
        except AttributeError:
            pass
