# This file is part of the DMComm project by BladeSabre. License: MIT.

import pulseio

from dmcomm.hardware.comms.modulated_shared import ModulatedParams, send, receive

class TalisCommunicator:
	def __init__(self, talis_input_output):
		self._pin = talis_input_output.pin
		self._params = None
		self._enabled = False
	def enable(self, signal_type):
		if self._enabled:
			if signal_type == self._params.signal_type:
				return
			self.disable()
		self._params = ModulatedParams(signal_type)
		self._enabled = True
	def disable(self):
		self._params = None
		self._enabled = False
	def reset(self):
		pass
	def send(self, bytes_to_send):
		if not self._enabled:
			raise RuntimeError("not enabled")
		output_pulses = pulseio.PulseOut(self._pin, frequency=100000, duty_cycle=0xFFFF)
		try:
			send(output_pulses, self._params, bytes_to_send)
		finally:
			output_pulses.deinit()
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		input_pulses = pulseio.PulseIn(self._pin, maxlen=600, idle_state=False)
		input_pulses.pause()
		try:
			bytes_received = receive(input_pulses, self._params, timeout_ms)
		finally:
			input_pulses.deinit()
		return bytes_received
