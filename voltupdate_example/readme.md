# VoltUpdate example:
- One of the simplest examples from the "NI-DAQmx ANSI C" collection
(typically located in C:\Users\Public\Documents\National Instruments\NI-DAQ\Examples\DAQmx ANSI C)
- It may be necessary to refer to the header file "NIDAQmx.h" and "NI_C_data_types.pdf" (included here)
 for additional information like input and output types for function calls, and error codes.
- The essential "nicaiu.dll" and reference "Which_dlls_contain_the_NI_DAQ_functions.pdf" are included
 for convenience.
- voltupdate_raw.py shows how a raw script is generated following the "VoltUpdate.c" example in a 
'line by line' style.
- voltupdate_tidy.py shows how to clean up the 'raw' script into a format that is closer to the device
adaptor "ni_PICe_6739.py"