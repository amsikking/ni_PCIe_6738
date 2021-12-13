''' Tidy program following the NI-DAQmx ANSI C example "VoltUpdate.c"'''
import ctypes as C
import numpy as np

dll = C.cdll.LoadLibrary("nicaiu")

### Succesful calls return '0' so let's write a basic check error function: ###
def check_error(error_code):
    if error_code != 0: # succesful calls return '0'
        raise Exception('dll error code: %i'%error_code)

### Tidy and store DLL calls away from main program with .argtypes/.restype: ###

dll.create_task = dll.DAQmxCreateTask
dll.create_task.argtypes = [C.c_char_p, C.POINTER(C.c_void_p)]
dll.create_task.restype = check_error

dll.create_ao_voltage_channel = dll.DAQmxCreateAOVoltageChan
dll.create_ao_voltage_channel.argtypes = [
    C.c_void_p,
    C.c_char_p,
    C.c_char_p,
    C.c_double,
    C.c_double,
    C.c_int32,
    C.c_char_p]
dll.create_ao_voltage_channel.restype = check_error

dll.start_task = dll.DAQmxStartTask
dll.start_task.argtypes = [C.c_void_p]
dll.start_task.restype = check_error

dll.write_voltages = dll.DAQmxWriteAnalogF64
dll.write_voltages.argtypes = [
    C.c_void_p,
    C.c_int32,
    C.c_uint32, # NI calls this a 'bool32'?
    C.c_double,
    C.c_uint32,
    np.ctypeslib.ndpointer(dtype=np.float64, ndim=2), # tricky...
    C.POINTER(C.c_int32),
    C.POINTER(C.c_uint32)]
dll.write_voltages.restype = check_error

dll.stop_task = dll.DAQmxStopTask
dll.stop_task.argtypes = [C.c_void_p]
dll.stop_task.restype = check_error

dll.clear_task = dll.DAQmxClearTask
dll.clear_task.argtypes = [C.c_void_p]
dll.clear_task.restype = check_error

### Main program ###

# "DAQmxCreateTask":-> reference "NI-DAQmx C Reference Help" and "Python ctypes"
taskHandle = C.c_void_p()
dll.create_task(bytes(), taskHandle)

# "DAQmxCreateAOVoltageChan":
physicalChannel = bytes('Dev1/ao0', 'ascii')
minVal = -10.0
maxVal = +10.0
dll.create_ao_voltage_channel(
    taskHandle, physicalChannel, bytes(), minVal, maxVal, 10348, bytes()) 

# "DAQmxStartTask":
dll.start_task(taskHandle)

# "DAQmxWriteAnalogF64":
# set: autoStart = 1, timeout = 10.0, dataLayout = 0 (DAQmx_Val_GroupByChannel)
numSampsPerChan = 1
writeArray = np.array(((1.0,),(0,)))
dll.write_voltages(
    taskHandle, numSampsPerChan, 1, 10.0, 0, writeArray, None, None)
input('check for 1v on channel 0, then hit enter for 0v...')

### Tidy up: set channel back to zero, stop and clear task ###
writeArray = np.array(((0.0,),(0,)))
dll.write_voltages(
    taskHandle, numSampsPerChan, 1, 10.0, 0, writeArray, None, None)
dll.stop_task(taskHandle)
dll.clear_task(taskHandle)

