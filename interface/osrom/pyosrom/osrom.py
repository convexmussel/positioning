""" NIDAQ OSROM control.
This module is used to control an NI DAQ to behave as an OSROM.
It makes use of the PyDAQmx module and thus the NI DAQmx SDK.
make sure to install the SDK and not the driver, this will not work.

About
-----
This modules defines two classes:

1. InputTask   - Creates an input, the data is read back from the
                 hardware every scan. If so, the new data flag will
                 be set and the data is available to be read.
2. OutputTask  - Creates an output, normally used to set the waveform.

Status
------
It is very hackish. Clean up needs to be done

Things to do
------------
add documentation
test
"""
# todo add documentation
# todo add tests

__author__ = "Gerald Ebberink"
__copyright__ = "Copyright 2016 - 2017"
__license__ = "GPLv2"
__version__ = "2.0.0"
__maintainer__ = "Gerald Ebberink"
__email__ = "g.h.p.ebberink@saxion.nl"
__status__ = "Prototype"

import configparser
import os
import sys
from _ctypes import byref

import numpy
try:
    import PyDAQmx
except Exception as e:
    print(e)
from piezo.util.project_root import get_project_root


# noinspection PyUnresolvedReferences,PyAttributeOutsideInit,PyPep8Naming
class InputTask(PyDAQmx.Task):
    """"The input task for the OSROM
    This class subclasses the PyDAQmx task.

    On startup the config file is read. If no file name is given it
    config_osrom.ini is used. The config file should be in the root of the
    program directory.

    Afterwards after every scan the data is stored in the data variable and the
    new_data flag is set.
    """
    def __init__(self, config_file=None):
        """Initial setup of the Input task
        This means that the data is reset as well as the new_data flag.
        Then the configuration file is read (either the hardcoded one or the
        one supplied as a parameter)
        """
        PyDAQmx.Task.__init__(self)
        self.StopTask()

        self.data = None
        self.new_data = False
        # get the relative path so it works on all operating systems
        rel_path = get_project_root()
        self.config_filename = os.path.join(rel_path, "interface", "osrom", "config", "config_osrom.ini")

        self.config = configparser.ConfigParser()

        self.load_config(config_file=config_file)
        # self.setup()

    # noinspection PyAttributeOutsideInit
    def load_config(self, config_file=None):
        """load a configuration file

        If no file is given the self.config_filename is used.
        This is then added after the path of the executed script (argv[0])

        After this the file is opened and the parts in the [input] are read.
        currently only:
        * device
        * channels
        * samples
        * sample_rate
        * max_voltage
        * min_voltage
        are supported.

        Then also some derived variables are calculated.
        """
        if config_file is not None:
            self.config_filename = config_file
        # load the config file
        self.config_path = os.path.join(
                os.path.abspath(os.path.dirname(sys.argv[0])),
                self.config_filename)
        self.config.read(self.config_path)

        # set the variables according to the config file.
        self.device = self.config.get("input", "device")
        self.input_channels = self.config.get("input", "channels").split(',')
        self.number_of_samples = self.config.getint("input", "samples")
        self.sample_rate = self.config.getint("input", "sample_rate")
        self.max_voltage = self.config.getfloat("input", "max_voltage")
        self.min_voltage = self.config.getfloat("input", "min_voltage")

        # set the variables derived from the variables read from the config
        # file
        self.number_of_channels = len(self.input_channels)

    def save_config(self, config_file=None):
        """save a configuration file

        If no file is given the self.config_filename is used.
        This is then added after the path of the executed script (argv[0])

        After this the configuration is made to match the current settings,
        and written to the file.
        currently only:
        * device
        * channels
        * samples
        * sample_rate
        * max_voltage
        * min_voltage
        are supported.

        Then also some derived variables are calculated.
        """
        if config_file is not None:
            self.config_filename = config_file
        self.config_path = os.path.join(os.path.abspath(
                os.path.dirname(sys.argv[0])),
                self.config_filename)

        self.config.set("input", "device", self.device)
        self.config.set("input", "channels", ','.join(self.output_channels))
        self.config.set("input", "samples", self.number_of_samples)
        self.config.set("input", "sample_rate", self.sample_rate)
        self.config.set("input", "max_voltage", self.max_voltage)
        self.config.set("input", "min_voltage", self.min_voltage)

        self.config.write(self.config_filename)

    def setup(self, device=None, input_channels=None,
              max_voltage=None, min_voltage=None):
        """Setup the measurement channels.
        """
        self.StopTask()
        if device is not None:
            self.device = device

        if input_channels is not None:
            self.input_channels = input_channels

        if max_voltage is not None:
            self.max_voltage = max_voltage

        if min_voltage is not None:
            self.min_voltage = min_voltage

        # concatenate the channels but first strip all the shite space
        # around the channel names.
        input_channels = [self.device + "/" + chan.strip()
                          for chan in self.input_channels]
        input_channels = ", ".join(input_channels)

        self.data = numpy.zeros([self.number_of_channels,
                                 self.number_of_samples],
                                dtype=numpy.float64
                                )
        self.CreateAIVoltageChan(input_channels,
                                 "",
                                 PyDAQmx.DAQmx_Val_RSE,
                                 numpy.float64(self.min_voltage),
                                 numpy.float64(self.max_voltage),
                                 PyDAQmx.DAQmx_Val_Volts,
                                 None
                                 )

        # Set the clock timings
        self.CfgSampClkTiming(None,
                              numpy.float64(self.sample_rate),
                              PyDAQmx.DAQmx_Val_Rising,
                              PyDAQmx.DAQmx_Val_ContSamps,
                              numpy.uint64(self.number_of_samples)
                              )

        # Make sure that when all the samples are acquired call EveryNCallback
        self.AutoRegisterEveryNSamplesEvent(
                PyDAQmx.DAQmx_Val_Acquired_Into_Buffer,
                self.number_of_samples,
                0
        )
        self.StartTask()

    def EveryNCallback(self):
        """This method is called every time all the samples are acquired"""
        read = PyDAQmx.int32()
        self.ReadAnalogF64(self.number_of_samples,
                           0,
                           PyDAQmx.DAQmx_Val_GroupByChannel,
                           self.data,
                           PyDAQmx.uInt32(self.data.size),
                           byref(read),
                           None)
        self.new_data = True


# noinspection PyAttributeOutsideInit
class OutputTask(PyDAQmx.Task):
    def __init__(self):
        PyDAQmx.Task.__init__(self)
        self.config_filename = r"config_osrom.ini"
        self.config = configparser.ConfigParser()
        self.load_config()
        self.setup()

    def load_config(self, file=None):
        if file is not None:
            self.config_filename = file

        rel_path = get_project_root()
        self.config_path = os.path.join(rel_path, "interface", "osrom", "config", "config_osrom.ini")

        # load the config file
        self.config.read(self.config_path)

        self.device = self.config.get("output", "device")
        self.output_channels = self.config.get("output", "channels").split(',')
        self.number_of_samples = self.config.getint("output", "samples")
        self.sample_rate = self.config.getint("output", "sample_rate")
        self.max_voltage = self.config.getfloat("output", "max_voltage")
        self.min_voltage = self.config.getfloat("output", "min_voltage")

        self._waveform = numpy.zeros([self.number_of_samples], dtype=numpy.float64)

    def save_config(self, file=None):
        if file is not None:
            self.config_filename = file

        self.config.set("output", "device", self.device)
        self.config.set("output", "channels", ','.join(self.output_channels))
        self.config.set("output", "samples", self.number_of_samples)
        self.config.set("output", "sample_rate", self.sample_rate)
        self.config.set("output", "max_voltage", self.max_voltage)
        self.config.set("output", "min_voltage", self.min_voltage)

        self.config.write(self.config_filename)

    def setup(self, device=None, output_channels=None,
              max_voltage=None, min_voltage=None):
        self.StopTask()
        if device is not None:
            self.device = device

        if output_channels is not None:
            self.output_channels = output_channels

        if max_voltage is not None:
            self.max_voltage = max_voltage

        if min_voltage is not None:
            self.min_voltage = min_voltage

        output_channels = [self.device + "/" + chan.strip() for chan in
                           self.output_channels]
        output_channels = ", ".join(output_channels)
        self.CreateAOVoltageChan(output_channels, "", numpy.float64(self.min_voltage),
                                 numpy.float64(self.max_voltage), PyDAQmx.DAQmx_Val_Volts, None)
        self.CfgOutputBuffer(PyDAQmx.uInt32(self.number_of_samples))
        self.CfgSampClkTiming("ai/SampleClock", numpy.float64(self.sample_rate), PyDAQmx.DAQmx_Val_Rising,
                              PyDAQmx.DAQmx_Val_ContSamps, numpy.uint64(self.number_of_samples))
        self._start_output()

    def _start_output(self):
        self.StopTask()
        samples_written = PyDAQmx.int32()
        self.WriteAnalogF64(PyDAQmx.int32(self.number_of_samples), False,
                            PyDAQmx.float64(25), PyDAQmx.DAQmx_Val_GroupByChannel,
                            self._waveform, byref(samples_written),
                            None)
        self.StartTask()

    @property
    def waveform(self):
        return self._waveform

    @waveform.setter
    def waveform(self, wave):
        self._waveform = wave
        self._start_output()
