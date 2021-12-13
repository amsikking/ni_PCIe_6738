''' Bare bones program following the NI-DAQmx ANSI C example "VoltUpdate.c"'''
import ctypes as C

dll = C.cdll.LoadLibrary("nicaiu")

### Succesful calls return '0' so let's write a basic check error function: ###
def check_error(error_code):
    if error_code != 0:
        raise Exception('dll error code: %i'%error_code)

### DAQmx Configure Code ###
# "DAQmxCreateTask":-> reference "NI-DAQmx C Reference Help" and "Python ctypes"
# type(taskName) = const char [] = C.c_char_p
taskName = C.c_char_p() # instance
# type(taskHandle) = TaskHandle * = (void*)* (found in NIDAQmx.h)
# = (C.c_void_p)* = C.POINTER(C.c_void_p) (from ctypes)
taskHandle = C.c_void_p()
taskHandle_pointer = C.POINTER(C.c_void_p)(taskHandle) # instance
check_error(dll.DAQmxCreateTask(taskName, taskHandle_pointer))

# "DAQmxCreateAOVoltageChan":
DAQmx_Val_Volts = 10348 # from "Pre-Scaled Units" section in C Ref Help...
name = bytes('Dev1/ao0', 'ascii')
physicalChannel = C.c_char_p(name)          # const char []
nameToAssignToChannel = C.c_char_p()        # const char []
minVal = C.c_double(-10.0)                  # float64
maxVal = C.c_double(+10.0)                  # float64
units = C.c_int(DAQmx_Val_Volts)            # int32
customScaleName = C.c_char_p()              # const char []
check_error(dll.DAQmxCreateAOVoltageChan(
    taskHandle, # handle, not pointer!
    physicalChannel,
    nameToAssignToChannel,
    minVal,
    maxVal,
    units,
    customScaleName,
    )) 

### DAQmx Start Code ###
# "DAQmxStartTask":
check_error(dll.DAQmxStartTask(taskHandle))

### DAQmx Write Code ###
# "DAQmxWriteAnalogF64":
DAQmx_Val_GroupByChannel = 0
data = ((1.0,),(0,))                                # value, channel
numSampsPerChan = C.c_int(1)                        # int32
autoStart = C.c_uint(1)                             # bool32, but needs uint?
timeout = C.c_double(10.0)                          # float64
dataLayout = C.c_uint(DAQmx_Val_GroupByChannel)     # bool32, but needs uint?
##writeArray = C.c_double(data)                     # float64 [] = 2d array?
import numpy as np # no 2d array from ctypes?
writeArray = np.ctypeslib.as_ctypes(np.array(data)) # tricky solution to find...
sampsPerChanWritten = C.c_int()
sampsPerChanWritten_pointer = (
    C.POINTER(C.c_int)(sampsPerChanWritten))        # int32*
reserved = C.c_uint()
reserved_pointer = C.POINTER(C.c_uint)(reserved)    # bool32*
check_error(dll.DAQmxWriteAnalogF64(
    taskHandle,
    numSampsPerChan,
    autoStart,
    timeout,
    dataLayout,
    writeArray,
    sampsPerChanWritten,
    reserved))
input('check for 1v on channel 0, then hit enter for 0v...')

### Tidy up: set channel back to zero, stop and clear task ###
data = ((0.0,),(0,))
writeArray = np.ctypeslib.as_ctypes(np.array(data))
check_error(dll.DAQmxWriteAnalogF64(
    taskHandle,
    numSampsPerChan,
    autoStart,
    timeout,
    dataLayout,
    writeArray,
    sampsPerChanWritten,
    reserved))
check_error(dll.DAQmxStopTask(taskHandle))
check_error(dll.DAQmxClearTask(taskHandle))
