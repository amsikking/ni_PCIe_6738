import ctypes as C
import numpy as np

class Analog_Out:
    def __init__(self, num_channels=32, rate=1e4, verbose=True):
        """Play analog voltages with a NI-DAQ PCIe-6738"""
        assert 1 <= num_channels <= 32
        self.num_channels = num_channels
        self.daq_type = '6738'
        self.max_rate = 1e6
        self.verbose = verbose
        if self.verbose: print("NI-DAQ-%s: opening..."%self.daq_type)
        self._task_running = False
        self.task_handle = C.c_void_p(0)
        dll.create_task(bytes(), self.task_handle)
        board_name = 'Dev1' # check with NI MAX (auto detect would be better)
        device_name = bytes(
            board_name + '/ao0:%i'%(self.num_channels - 1), 'ascii')
        dll.create_ao_voltage_channel(
            self.task_handle,
            device_name,
            b"",
            -10,    # Minimum voltage
            +10.0,  # Maximum voltage
            10348,  # DAQmx_Val_Volts = conversion factor
            None)   # NULL
        self.board_name = board_name
        self.voltages = np.zeros((2, self.num_channels), 'float64')
        self.set_rate(rate)
        self._write_voltages(self.voltages)
        self.play_voltages(force_final_zeros=False, block=True)
        if self.verbose: print("NI-DAQ-%s: opened and ready.\n"%self.daq_type)

    def s2p(self, seconds): # convert time in seconds to ao 'pixels'
        num_pixels = int(round(self.rate * seconds))
        return num_pixels

    def p2s(self, num_pixels): # convert ao 'pixels' to time in seconds
        seconds = num_pixels / self.rate
        return seconds

    def s2s(self, seconds): # legalize seconds to a value the ao can deliver
        seconds = self.p2s(self.s2p(seconds))
        return seconds

    def set_rate(self, rate):
        self._ensure_task_is_stopped()
        assert 0 < rate <= self.max_rate
        self.rate = float(rate)
        dll.clock_timing(
            self.task_handle,
            None,                   # NULL = internal clock for timing
            self.rate,
            10280,                  # DAQmx_Val_Rising = generate on rising edge
            10178,                  # DAQmx_Val_FiniteSamps = finite samples
            self.voltages.shape[0]) # number of samples
        return None

    def play_voltages(
        self,
        voltages=None,          # =None: plays the previously set voltages
        force_final_zeros=True, # =True: last entry on all voltage channels -> 0
        block=True,             # =True: waits until voltage play is finished
        ):
        self._ensure_task_is_stopped() # must wait for previous play_voltages()
        if voltages is not None:
            self._write_voltages(voltages, force_final_zeros)
        if self.verbose: print("NI-DAQ-%s: playing voltages..."%self.daq_type)
        dll.start_task(self.task_handle)
        self._task_running = True
        if block:
            self._ensure_task_is_stopped()
        return None

    def _write_voltages(self, voltages, force_final_zeros=True):
        assert len(voltages.shape) == 2
        assert voltages.dtype == self.voltages.dtype
        assert voltages.shape[0] >= 2 # at least 2 samples for force_final_zeros
        assert voltages.shape[1] == self.num_channels
        if self.verbose:
            print("NI-DAQ-%s: writing voltages..."%self.daq_type, end='')
        if force_final_zeros:
            if self.verbose:
                print("(forcing final voltages to zero)", end='')
            voltages[-1, :] = 0
        old_voltages_shape = self.voltages.shape
        self.voltages = voltages
        if self.voltages.shape[0] != old_voltages_shape[0]:
            self.set_rate(self.rate) # must update sample number if changed
        if not hasattr(self, 'num_points_written'):
            self.num_points_written = C.c_int32(0)
        self._ensure_task_is_stopped()
        dll.write_voltages(
            self.task_handle,
            self.voltages.shape[0], # Samples per channel
            0,                      # Autostart = False
            10.0,                   # Timeout in seconds
            1,                      # DAQmx_Val_GroupByScanNumber (interleaved)
            self.voltages,
            self.num_points_written,
            None)
        if self.verbose:
            print("\n-> %i points written to each channel."%(
                self.num_points_written.value))
        return None

    def _ensure_task_is_stopped(self):
        if self._task_running:
            if self.verbose:
                print("NI-DAQ-%s: waiting to finish play..."%self.daq_type,
                      end='')
            dll.finish_task(self.task_handle, -1)
            if self.verbose: print(" done.")
            dll.stop_task(self.task_handle)
            self._task_running = False
        return None

    def close(self):
        # TODO: make it harder to forget .close() which can leave persistant
        # voltages. _del_? _enter_ and _exit_?
        self._ensure_task_is_stopped()
        if self.verbose: print("NI-DAQ-%s: closing..."%self.daq_type)
        dll.clear_task(self.task_handle)
        if self.verbose: print("NI-DAQ-%s: closed."%self.daq_type)
        return None

### Tidy and store DLL calls away from main program:

dll = C.cdll.LoadLibrary("nicaiu") # needs "nicaiu.dll" in os.environ['PATH']

dll.get_error_info = dll.DAQmxGetExtendedErrorInfo
dll.get_error_info.argtypes = [C.c_char_p, C.c_uint32]

def check_error(error_code):
    if error_code != 0:
        num_bytes = dll.get_error_info(None, 0)
        print("Error message from NI-DAQ: (", num_bytes, "bytes )")
        error_buffer = (C.c_char * num_bytes)()
        dll.get_error_info(error_buffer, num_bytes)
        print(error_buffer.value.decode('ascii'))
        raise UserWarning(
            "NI-DAQ error code: %i; see above for details."%(error_code))
    return error_code

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

dll.create_do_channel = dll.DAQmxCreateDOChan
dll.create_do_channel.argtypes = [
    C.c_void_p,
    C.c_char_p,
    C.c_char_p,
    C.c_int32]
dll.create_do_channel.restype = check_error

dll.clock_timing = dll.DAQmxCfgSampClkTiming
dll.clock_timing.argtypes = [
    C.c_void_p,
    C.c_char_p,
    C.c_double,
    C.c_int32,
    C.c_int32,
    C.c_uint64]
dll.clock_timing.restype = check_error

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

dll.start_task = dll.DAQmxStartTask
dll.start_task.argtypes = [C.c_void_p]
dll.start_task.restype = check_error

dll.finish_task = dll.DAQmxWaitUntilTaskDone
dll.finish_task.argtypes = [C.c_void_p, C.c_double]
dll.finish_task.restype = check_error

dll.stop_task = dll.DAQmxStopTask
dll.stop_task.argtypes = [C.c_void_p]
dll.stop_task.restype = check_error

dll.clear_task = dll.DAQmxClearTask
dll.clear_task.argtypes = [C.c_void_p]
dll.clear_task.restype = check_error

if __name__ == '__main__':
    ao = Analog_Out(num_channels=1, rate=1e6, verbose=True)
    play_s = 1

    print('\nVoltage step:')
    volts = np.zeros((ao.s2p(play_s), ao.num_channels), 'float64')
    volts[ao.s2p(0.25 * play_s):ao.s2p(.75 * play_s), :] = 1
    ao.play_voltages(volts, block=False)

    print('\nSine wave: (forces finish of previous play)')
    volts = np.zeros((ao.s2p(play_s), ao.num_channels), 'float64')
    periods = 100
    wave = np.sin(np.linspace(0, periods * np.pi, volts.shape[0]))
    volts[:, :] = wave.reshape(volts.shape[0], 1)
    ao.play_voltages(volts)
    
    ao.close()
