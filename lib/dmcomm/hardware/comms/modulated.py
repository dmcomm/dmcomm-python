# This file is part of the DMComm project by BladeSabre. License: MIT.

import pulseio

from dmcomm.hardware.comms.modulated_shared import ModulatedParams, send, receive

class ModulatedCommunicator:
	def __init__(self, ir_output, ir_input_modulated):
		self._pin_output = ir_output.pin_output
		self._pin_input = ir_input_modulated.pin_input
		self._output_pulses = None
		self._input_pulses = None
		self._params = None
		self._enabled = False
	def enable(self, signal_type):
		if self._enabled:
			if signal_type == self._params.signal_type:
				return
			self.disable()
		self._params = ModulatedParams(signal_type)
		try:
			self._output_pulses = pulseio.PulseOut(self._pin_output, frequency=38000, duty_cycle=0x8000)
			self._input_pulses = pulseio.PulseIn(self._pin_input, maxlen=300, idle_state=True)
			self._input_pulses.pause()
		except:
			self.disable()
			raise
		self._enabled = True
	def disable(self):
		for item in [self._output_pulses, self._input_pulses]:
			if item is not None:
				item.deinit()
		self._ouput_pulses = None
		self._input_pulses = None
		self._params = None
		self._enabled = False
	def reset(self):
		pass
	def send(self, bytes_to_send):
		if not self._enabled:
			raise RuntimeError("not enabled")
		send(self._output_pulses, self._params, bytes_to_send)
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		return receive(self._input_pulses, self._params, timeout_ms)
