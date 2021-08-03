# This file is part of the DMComm project by BladeSabre. License: MIT.

import supervisor

WAIT_FOREVER = -2
WAIT_REPLY = -1

class CommandError(ValueError):
	pass

class ReceiveError(Exception):
	pass

# Example from https://circuitpython.readthedocs.io/en/latest/shared-bindings/supervisor/index.html
_TICKS_PERIOD = const(1<<29)
_TICKS_MAX = const(_TICKS_PERIOD-1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)
def ticks_diff(ticks1, ticks2):
	"Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
	diff = (ticks1 - ticks2) & _TICKS_MAX
	diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
	return diff

def wait_for_length(obj, target, timeout_ms):
	start_ticks_ms = supervisor.ticks_ms()
	while True:
		if len(obj) >= target:
			return True
		passed_ms = ticks_diff(supervisor.ticks_ms(), start_ticks_ms)
		if timeout_ms != WAIT_FOREVER and passed_ms >= timeout_ms:
			return False

def wait_for_length_2(obj, target, start_timeout_ms, dur_timeout_ms):
	if not wait_for_length(obj, 1, start_timeout_ms):
		return False
	return wait_for_length(obj, target, dur_timeout_ms)
