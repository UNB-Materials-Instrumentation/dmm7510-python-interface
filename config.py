# config.py

"""
Configuration for connecting to the Keithley DMM7510 over USB using NI-VISA.

If VISA_RESOURCE is left as an empty string, the code will automatically use
the *first* VISA instrument it finds (e.g. 'USB0::0x05E6::0x7510::...::INSTR').

If you want to be explicit, run a small script to print rm.list_resources()
and paste the exact resource string here.
"""

VISA_RESOURCE: str = "USB0::0x05E6::0x7510::04647223::INSTR"
