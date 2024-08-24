# This file is part of the DMComm project by BladeSabre. License: MIT.

import array
import pulseio

from dmcomm import CommandError
from dmcomm.protocol.barcode import ean13_lengths

class BarcodeCommunicator:
	def __init__(self, ir_output):
		self._pin_output = ir_output.pin_output
		self._output_pulses = None
		self._enabled = False
	def enable(self, signal_type):
		if self._enabled:
			return
		try:
			self._output_pulses = pulseio.PulseOut(self._pin_output, frequency=100_000, duty_cycle=0xF000)
		except:
			self.disable()
			raise
		self._enabled = True
	def disable(self):
		if self._output_pulses is not None:
			self._output_pulses.deinit()
		self._output_pulses = None
		self._enabled = False
	def reset(self):
		pass
	def send(self, digits_to_send):
		if not self._enabled:
			raise RuntimeError("not enabled")
		if len(digits_to_send) != 13:
			raise CommandError("requires 13 digits")
		array_to_send = array.array("H", [0xFFFF])
		for length in ean13_lengths(digits_to_send):
			array_to_send.append(length * 1000)
		array_to_send.append(0xFFFF)
		self._output_pulses.send(array_to_send)
	def receive(self, timeout_ms):
		return []
