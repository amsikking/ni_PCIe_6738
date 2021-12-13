# ni_PCIe_6738
Python device adaptor: National Instruments 16-Bit, 32 Channels, 1 MS/s Analog Output Device
## Quick start:
- Install the NI-DAQ PCIe-6738 board, then the "NI-DAQmx" driver and then run "ni_PICe_6739.py" 
to generate voltages (requires Python and numpy).
## Details:
- National Instruments (NI) makes many "data acquisition systems" (DAQ's) often refered to as NI-DAQ's.
These PC controlled devices offer many options for analogue and digital input/output (ai/ao/di/do), with
varying numbers of channels, channel speeds and channel bit depths. They are therefore a powerful and
flexible tool for measuring or controlling many external devices for many applications.
- Many NI-DAQ's use the common driver software "NI-DAQmx" (a free download which must be installed).
There are many ways to interact with NI-DAQmx (NI LabVIEW, ANSI C, Microsoft Visual C++, 
Microsoft C# .NET, Microsoft Visual Basic .NET, Microsoft Visual Basic 6.0, Python, etc).
- The Python project "nidaqmx" offers a "a complex, highly object-oriented wrapper around the 
NI-DAQmx C API using the ctypes Python library" and is worth considering.
- Here we choose to implement our own 'minimal' Python wrapper using the "ANSI C" application programming
interface (API) which gives maximum control and flexibility over how much of the underlying C API is
exposed, and how our resulting Python API will be presented to the end user.
- To do this we will make 'function calls' to the dynamic link library (DLL) "nicaiu.dll". This file is 
installed and registered during the NI-DAQmx install (typically located "C:\Windows\System32\nicaiu.dll")
and contains the NI-DAQmx ANSI C API.
- To see what functions calls are available and how to use them see the "NI-DAQmx C Reference Help"
(typically found with "Start»Programs»National Instruments»NI-DAQ»NI-DAQmx C Reference Help"). For more
general help check out "NI-DAQmx Help" (same location) or search online.
- To get started on how to combine function calls into a program check out the collection
of "NI-DAQmx ANSI C" examples like the "VoltUpdate.c" included in this repository
