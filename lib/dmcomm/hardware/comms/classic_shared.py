# This file is part of the DMComm project by BladeSabre. License: MIT.

import digitalio
import pulseio
import rp2pio

from dmcomm.hardware import pio_programs

class BaseProngCommunicator:
	def __init__(self, prong_output, prong_input):
		self._pin_drive_signal = prong_output.pin_drive_signal
		self._pin_weak_pull = prong_output.pin_weak_pull
		self._pin_input = prong_input.pin_input
		self._output_state_machine = None
		self._output_weak_pull = None
		self._input_pulses = None
		self._params = None
		self._enabled = False
	def enable(self, signal_type):
		if self._enabled:
			if signal_type == self._params.signal_type:
				return
			self.disable()
		self._params = self.params_class(signal_type)
		try:
			self._output_state_machine = rp2pio.StateMachine(
				pio_programs.prong_TX,
				frequency=1_000_000,
				first_set_pin=self._pin_drive_signal,
				set_pin_count=2,
				initial_set_pin_direction=0,
			)
			self._output_weak_pull = digitalio.DigitalInOut(self._pin_weak_pull)
			self._output_weak_pull.switch_to_output(value=self._params.idle_state)
			self._input_pulses = pulseio.PulseIn(self._pin_input, maxlen=260, idle_state=self._params.idle_state)
			self._input_pulses.pause()
		except:
			self.disable()
			raise
		self._enabled = True
	def disable(self):
		for item in [self._output_state_machine, self._output_weak_pull, self._input_pulses]:
			if item is not None:
				item.deinit()
		self._output_state_machine = None
		self._output_weak_pull = None
		self._input_pulses = None
		self._params = None
		self._enabled = False
