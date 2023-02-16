# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.hardware`
=================
Communication with pronged and infrared Digimon toys, for CircuitPython on RP2040.

Note: This API is still under development and may change at any time.
"""

#: Value to pass to receiving functions indicating there is no timeout.
WAIT_FOREVER = -2

#: Value to pass to receiving functions indicating the default reply timeout.
WAIT_REPLY = -1

from .control import Controller
from .pins import ProngOutput, ProngInput, InfraredOutput, InfraredInputModulated, InfraredInputRaw, TalisInputOutput

__all__ = [
	"WAIT_FOREVER", "WAIT_REPLY", "Controller",
	"ProngOutput", "ProngInput", "InfraredOutput", "InfraredInputModulated", "InfraredInputRaw", "TalisInputOutput"
	]
