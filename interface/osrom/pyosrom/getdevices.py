
try:
    import PyDAQmx
except Exception as e:
    print(e)
import ctypes

# static method, because it does not act on the class
def getdevices():
    """Returns a list of all the DAQ devices available"""
    # list all devices
    buffer_size = ctypes.c_uint32(512)
    data = ctypes.create_string_buffer(512)
    PyDAQmx.DAQmxGetSysDevNames(data, buffer_size)
    return data.value
