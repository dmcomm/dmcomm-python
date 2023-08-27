# This file is part of the DMComm project by BladeSabre. License: MIT.

import supervisor

from dmcomm import ReceiveError
from . import WAIT_FOREVER

# Example from https://circuitpython.readthedocs.io/en/latest/shared-bindings/supervisor/index.html
_TICKS_PERIOD = 1 << 29
_TICKS_MAX = _TICKS_PERIOD - 1
_TICKS_HALFPERIOD = _TICKS_PERIOD // 2
def ticks_diff(ticks1, ticks2):
	"Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
	diff = (ticks1 - ticks2) & _TICKS_MAX
	diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
	return diff

def wait_for_length(obj, target, timeout_ms):
	"""Wait for `obj` to have length >= `target` with timeout in milliseconds.

	Returns True if target length was reached in time, False otherwise.
	Note for PulseIn that length 1 is reached on the second edge, not the first!
	"""
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

def wait_for_length_no_more(obj, start_timeout_ms, dur_timeout_ms, no_more_timeout_ms):
	if not wait_for_length(obj, 1, start_timeout_ms):
		return False
	prev_length = len(obj)
	start_ticks_ms = supervisor.ticks_ms()
	prev_ticks_ms = start_ticks_ms
	while True:
		now_length = len(obj)
		now_ticks_ms = supervisor.ticks_ms()
		if now_length != prev_length:
			prev_length = now_length
			prev_ticks_ms = now_ticks_ms
		if ticks_diff(now_ticks_ms, prev_ticks_ms) > no_more_timeout_ms:
			return True
		if ticks_diff(now_ticks_ms, start_ticks_ms) > dur_timeout_ms:
			return True #cut it off before it was done, but not worrying about that for now

def pop_pulse(pulses, empty_error_code):
	if len(pulses) == 0:
		raise ReceiveError(str(empty_error_code))
	return pulses.popleft()
