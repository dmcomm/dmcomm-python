# This file is part of the DMComm project by BladeSabre. License: MIT.

import digitalio
import pulseio
import rp2pio

from . import pio_programs

class ProngCommunicator:
	def __init__(self, prong_output, prong_input):
		self._pin_drive_signal = prong_output.pin_drive_signal
		self._pin_weak_pull = prong_output.pin_weak_pull
		self._pin_input = prong_input.pin_input
		self._output_state_machine = None
		self._output_weak_pull = None
		self._input_pulsein = None
		self._protocol = None
	def enable(self, protocol):
		self.disable()
		if protocol in ["V", "X"]:
			self._idle_state = True
		elif protocol == "Y":
			self._idle_state = False
		else:
			raise ValueError("protocol must be V/X/Y")
		try:
			self._output_state_machine = rp2pio.StateMachine(
				pio_programs.prong_TX,
				frequency=1_000_000,
				first_set_pin=self._pin_drive_signal,
				set_pin_count=2,
				initial_set_pin_direction=0,
			)
			self._output_weak_pull = digitalio.DigitalInOut(self._pin_weak_pull)
			self._output_weak_pull.switch_to_output(value=idle_state)
			self._input_pulsein = pulseio.PulseIn(self._pin_input, maxlen=40, idle_state=idle_state)
		except:
			self.disable()
			raise
		self._protocol = protocol
	def disable(self):
		for item in [self._output_state_machine, self._output_weak_pull, self._input_pulsein]:
			if item is not None:
				item.deinit()
		self._ouput_state_machine = None
		self._output_weak_pull = None
		self._input_pulsein = None
		self._protocol = None
	def send(self, bits):
		pass
	def receive(self):
		pass
