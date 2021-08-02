# This file is part of the DMComm project by BladeSabre. License: MIT.

import digitalio
import pulseio
import rp2pio

from . import pio_programs

class ProngOutput:
	def __init__(self, pin_drive_signal, pin_weak_pull):
		#pin_drive_low must be pin_drive_signal+1
		self._pin_drive_signal = pin_drive_signal
		self._pin_weak_pull = pin_weak_pull
		self._state_machine = None
		self._out_weak_pull = None
	def enable(self, idle_state):
		self.disable()
		try:
			self._state_machine = rp2pio.StateMachine(
				pio_programs.prong_TX,
				frequency=1_000_000,
				first_set_pin=self._pin_drive_signal,
				set_pin_count=2,
				initial_set_pin_direction=0,
			)
			self._out_weak_pull = digitalio.DigitalInOut(self._pin_weak_pull)
			self._out_weak_pull.switch_to_output(value=idle_state)
		except:
			self.disable()
			raise
		print("test")
	def disable(self):
		for item in [self._state_machine, self._out_weak_pull]:
			if item is not None:
				item.deinit()
		self._state_machine = None
		self._out_weak_pull = None
	def send(self, data):
		self._state_machine.write(data)
