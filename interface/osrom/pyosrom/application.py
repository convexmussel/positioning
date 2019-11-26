"""This is the GUI interface for research purposes
It plots all the graphs and is very flexible.

The current version has the ability to store HDF5 files for future reference
"""
# todo implement temperature control
# todo implement calibration
# todo test FFT
# todo remove peak graph (we mostly use shift)
# todo use buffers for display

__author__ = "Gerald Ebberink"
__copyright__ = "Copyright 2016-2019"
__version__ = "2.0.0"
__maintainer__ = "Gerald Ebberink"
__email__ = "g.h.p.ebberink@saxion.nl"
__status__ = "Prototype"

import configparser
from piezo.interface.osrom.pyosrom.getdevices import getdevices
import numpy
import os
from piezo.util.project_root import get_project_root

# get the relative path so it works on all operating systems
rel_path = get_project_root()
folder_path = os.path.join(rel_path, "interface", "osrom", "config", "config_osrom.ini")

# import the correct osrom module given by the config.ini file
config = configparser.ConfigParser()
config.read(folder_path)
try:
    device = str.lower(config.get("application", "source"))
except configparser.NoSectionError:
    print("osrom not connected")

from piezo.interface.osrom.pyosrom import osrom

del config


# noinspection PyAttributeOutsideInit,PyUnresolvedReferences,PyUnusedLocal
class Osrom:
    def __init__(self, file=None):
        """ This is the main window.
        During initialisation it will read the config file. If no file name
        is given it will use 'config.ini'
        And set every thing accordingly
        """

        # get the relative path so it works on all operating systems
        rel_path = get_project_root()
        folder_path = os.path.join(rel_path, "interface", "osrom", "config", "config_osrom.ini")
        self.config_filename = folder_path
        self.config = configparser.ConfigParser()
        self.recording = False
        self.load_config(file=file)
        # a list of processors, since they might be history aware
        self.processors = []
        self.clear_data = True

        self.setup_measurement()

    def is_connected(self):
        devices = getdevices()
        if self.input_device.encode() in devices and self.output_device.encode() in devices:
            return True
        return False

    def load_config(self, file=None):
        """"Load the configuration values from the ini file
        If file is None, the internally stored value config_filename is
        used. It loads the values from the [application] part.
        """
        if file is not None:
            self.config_filename = file

        # if we are recording stop doing that.
        # it makes no sense when new and other values are taken (other
        # amount of channels, drive currents etc.)
        if self.recording:
            self.record_button_clicked()

        # load the config file
        self.config.read(self.config_filename)

        # since we are loading a new config, reset all graphs etc.
        self.pd_curves = []
        self.result_curves = []
        self.shift_curves = []
        self.peaks = []
        self.shifts = []
        self.processors = []
        self.mean_s = [["Channel", "Value"]]
        self.initial_update = True
        self.first_data = True
        self.sample_number = 0

        # read the application values
        self.data_filename = self.config.get("application", "data_file")
        self.peak_algorithm = self.config.getint("application", "algorithm")
        self.start_voltage = self.config.getfloat("application", "start")
        self.stop_voltage = self.config.getfloat("application", "stop")
        self.max_channels = self.config.getint("application", "max_channels")
        self.store_raw = self.config.getboolean("application", "store_raw")
        self.store_shift = self.config.getboolean("application", "store_shift")
        self.store_output = self.config.getboolean("application", "store_data")
        self.waveform_file = self.config.get("application", "waveform_file")
        self.buffer_size = self.config.getint("application",
                                              "max_shift_display")
        self.cut_data = self.config.getint("application", "cut_data")
        self.roll_data = self.config.get("application", "roll_data")
        self.scan_skip = self.config.getint("application", "scan_skip")
        self.input_device = self.config.get("input", "device")
        self.output_device = self.config.get("output", "device")
        self.device = self.config.get("application", "source")

        # the config only gets the string for waveform_file, if the string is
        # None we should translate that to the None value
        if self.waveform_file.lower() == "none":
            self.waveform_file = None

        if self.roll_data.lower() == "true":
            self.roll_data = True
        elif self.roll_data.lower() == "false":
            self.roll_data = numpy.int64(0)
        else:
            self.roll_data = numpy.int64(self.roll_data)

        # the config for the source can be many things
        self.device = str.lower(self.device)
        if self.device not in ["osrom", "piosrom"]:
            self.device = "virtual"

    def save_config(self, file=None):
        """"Save the configuration values to a file
        If file is None, the internally stored value config_filename is
        used. It writes the values to the [application] part.
        """
        if file is not None:
            self.config_filename = file

        # set the config according to the values in the application
        self.config.set("application", "datafile", self.data_filename)
        self.config.set("application", "algorithm", self.peak_algorithm)
        self.config.set("application", "start", self.start_voltage)
        self.config.set("application", "stop", self.stop_voltage)
        self.config.set("application", "max_channels", self.max_channels)
        self.config.set("application", "source", self.device)

        # write out to file
        self.config.write(self.config_filename)

    def _setup_intask(self, device=None, input_channels=None,
                      sample_rate=None, n_samples=None):
        """This function sets up the input task.
        Any arguments not None will be changed"""
        if device is not None:
            self.intask.device = device

        if input_channels is not None:
            # somehow the legends are not emptied
            for channel in self.intask.input_channels:
                channel = channel.strip()
                self.pd_legend.removeItem(channel)
                self.shift_legend.removeItem(channel)
            self.intask.input_channels = input_channels
            self.intask.number_of_channels = len(input_channels)

        if sample_rate is not None:
            self.intask.sample_rate = sample_rate

        if n_samples is not None:
            self.intask.number_of_samples = n_samples

        self.intask.setup()

    def _setup_outtask(self, device=None, output_channels=None,
                       sample_rate=None, n_samples=None,
                       v_min=None, v_max=None, waveform_file=None, ):
        """This function sets up the output task
        Any arguments which are not None will be changed
        Where waveform_file will override the v_min and v_max"""
        if device is not None:
            self.outtask.device = device
        if output_channels is not None:
            self.outtask.output_channels = output_channels
        if sample_rate is not None:
            self.outtask.sample_rate = sample_rate
        if n_samples is not None:
            self.outtask.number_of_samples = n_samples
        if v_min is not None and v_max is not None:
            self.outtask.waveform = numpy.linspace(
                    v_min, v_max,
                    self.outtask.number_of_samples,
                    dtype=numpy.float64)
        if waveform_file is not None:
            self.waveform_file = waveform_file

        # if an waveform file is given, load the second
        # column for the waveform
        # todo make sure we can also load information from a h5 file
        if self.waveform_file is not None:
            # to convert between comma and dot as decimal separator
            # we use a custom converter
            converter = {1: lambda s: float(s.decode().replace(',', '.'))}
            waveform = numpy.loadtxt(self.waveform_file,
                                     skiprows=1,
                                     usecols=(1,),
                                     converters=converter)
            self.outtask.waveform = waveform

    def setup_measurement(self, input_channels=None):
        """This sets the measurements up, initializes the input and output
        tasks, as well as the GUI."""
        # get the list of connected NI devices
        if self.device == "osrom":

            devices = getdevices()
            # if there is a device
            if devices:
                # check if the one of the connected devices is the one for input
                if self.input_device.encode() in devices:
                    # try to stop and clear the Task
                    try:
                        self.intask.StopTask()
                        self.intask.ClearTask()
                    except AttributeError:
                        # Ignore the error which is raised when there is no task
                        #  yet
                        pass
                    # create the task and set it up.
                    self.intask = osrom.InputTask()
                    self._setup_intask(input_channels=input_channels)
                else:
                    raise Exception("Input device not found")

                # check if the one of the connected devices is the one for output
                if self.output_device.encode() in devices:
                    # try to stop and clear the Task
                    try:
                        self.outtask.StopTask()
                        self.outtask.ClearTask()
                    except AttributeError:
                        # Ignore the error which is raised when there is no task
                        #  yet
                        pass
                    # create the task and set it up.
                    self.outtask = osrom.OutputTask()
                    self._setup_outtask(v_max=self.stop_voltage,
                                        v_min=self.start_voltage)

                else:
                    raise Exception("Output device not found")
            else:
                raise Exception("Output device not found")
        elif self.device == "piosrom":
            self.intask = osrom.InputTask()
            self.outtask = osrom.OutputTask()
            self._setup_intask(input_channels=input_channels)
            self._setup_outtask()
        elif self.device == "virtual":
            self.intask = osrom.InputTask()
            self.outtask = osrom.OutputTask()
            self._setup_intask(input_channels=input_channels)
            self._setup_outtask()

    def get_measurement(self):
        # check to see if there is new data available, if so process this.
        #alwasy return values even when ignoring the first 2
        while True:
            self.intask.new_data = False
            while self.intask.new_data is False:
                pass
            self.intask.new_data = False
            self.sample_number = self.sample_number + 1
            if self.sample_number > self.scan_skip:
                data = self.intask.data
                if isinstance(self.roll_data, numpy.int64):
                    data = numpy.roll(data, self.roll_data, 1)
                channels = self.intask.number_of_channels
                shift = numpy.nan
                # for all channels to be read
                return numpy.mean(data, axis=1)

    def disconnect(self):
        self.intask.StopTask()
        self.outtask.StopTask()
