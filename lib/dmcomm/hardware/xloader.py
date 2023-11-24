# This file is part of the DMComm project by BladeSabre. License: MIT.

import array
import board
import pulseio
import time
import rp2pio
import adafruit_pioasm

from dmcomm import ReceiveError
from . import WAIT_REPLY
from . import misc
from . import pio_programs

# Connect InfraredOutput to GP4, probe GP5
# Connect InfraredInputRaw to GP6, probe GP7
# Won't work with screen on default pins.
# Requires adafruit_pioasm.

program_xros = adafruit_pioasm.assemble("""
	pull
	mov osr ~ osr
	set pins 1 [4]
	set pins 0 [3]
	set x 7
loop:
	out pins 1
	set pins 0 [7]
	jmp x-- loop
	set x 24
delay_x:
	set y 31
delay_y:
	jmp y-- delay_y [1]
	jmp x-- delay_x
""")

program_extend_low = adafruit_pioasm.assemble("""
	set pins 1
is_high:
	jmp pin is_high
	set pins 0
	set x 31
delay_x:
	set y 31
delay_y:
	jmp y-- delay_y
	jmp x-- delay_x
""")

program_extend_high = adafruit_pioasm.assemble("""
	set pins 0
is_low:
	jmp pin is_high
	jmp is_low
is_high:
	set pins 1
	set x 31
delay_x:
	set y 31
delay_y:
	jmp y-- delay_y
	jmp x-- delay_x
""")

class XLoaderCommunicator:
	def __init__(self, ir_output, ir_input_raw):
		self._pin_output = ir_output.pin_output
		self._pin_input = ir_input_raw.pin_input
		self._output_state_machine = None
		self._input_pulses = None
		self._probe_high = None
		self._probe_low = None
		self._params = XLoaderParams()
		self._enabled = False
	def enable(self, signal_type):
		if self._enabled:
			if signal_type == self._params.signal_type:
				return
			self.disable()
		self._params.set_signal_type(signal_type)
		try:
			self._output_state_machine = rp2pio.StateMachine(
				program_xros,
				frequency=self._params.pio_clock,
				first_out_pin=self._pin_output,
				first_set_pin=self._pin_output,
			)
			self._input_pulses = pulseio.PulseIn(self._pin_input, maxlen=7000, idle_state=True)
			self._input_pulses.pause()
			self._probe_high = rp2pio.StateMachine(
				program_extend_high,
				frequency=1_000_000,
				jmp_pin=board.GP4,
				first_set_pin=board.GP5,
			)
			self._probe_low = rp2pio.StateMachine(
				program_extend_low,
				frequency=1_000_000,
				jmp_pin=board.GP6,
				first_set_pin=board.GP7,
			)
		except:
			self.disable()
			raise
		self._enabled = True
	def disable(self):
		for item in [self._output_state_machine, self._input_pulses, self._probe_high, self._probe_low]:
			if item is not None:
				item.deinit()
		self._ouput_state_machine = None
		self._input_pulses = None
		self._probe_high = None
		self._probe_low = None
		self._enabled = False
	def send(self, data):
		if not self._enabled:
			raise RuntimeError("not enabled")
		self._output_state_machine.write(bytes(data))
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		bytes_received = self.receive_bytes(timeout_ms)
		return bytes_received
	def receive_bytes(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		pulses = self._input_pulses
		pulses.clear()
		pulses.resume()
		if timeout_ms == WAIT_REPLY:
			timeout_ms = self._params.reply_timeout_ms
		misc.wait_for_length_no_more(pulses, timeout_ms,
			self._params.packet_length_timeout_ms, self._params.packet_continue_timeout_ms)
		pulses.pause()
		if len(pulses) == pulses.maxlen:
			raise ReceiveError("buffer full")
		if len(pulses) == 0:
			return []
		bytes_received = []
		current_byte = 0
		pulse_count = 0
		ticks_into_byte = 0
		ended = False
		while not ended:
			pulse_count += 1
			if len(pulses) == 0:
				raise ReceiveError("ended with gap")
			t_pulse = pulses.popleft()
			if t_pulse > self._params.pulse_max:
				raise ReceiveError("pulse %d = %d" % (pulse_count, t_pulse))
			if len(pulses) != 0:
				t_gap = pulses.popleft()
			else:
				t_gap = 0xFFFF
				ended = True
			dur = t_pulse + t_gap
			ticks = round(dur / self._params.tick_length)
			dur_rounded = ticks * self._params.tick_length
			off_rounded = abs(dur - dur_rounded)
			if ticks_into_byte + ticks >= 9:
				#finish byte
				for i in range(8 - ticks_into_byte):
					current_byte >>= 1
					current_byte |= 0x80
				bytes_received.append(current_byte)
				current_byte = 0
				ticks_into_byte = 0
			elif off_rounded > self._params.tick_margin:
				raise ReceiveError("pulse+gap %d = %d" % (pulse_count, dur))
			else:
				for i in range(ticks - 1):
					current_byte >>= 1
					current_byte |= 0x80
				current_byte >>= 1
				ticks_into_byte += ticks
		return bytes_received

class XLoaderParams:
	def __init__(self):
		self.set_signal_type("!XL")
	def set_signal_type(self, signal_type):
		if signal_type == "!XL":
			self.pio_clock = 583430
			self.reply_timeout_ms = 1000
			self.packet_length_timeout_ms = 1000
			self.packet_continue_timeout_ms = 3
			self.pulse_max = 250
			self.tick_length = 17
			self.tick_margin = 5
		else:
			raise ValueError("signal_type must be !XL")
		self.signal_type = signal_type
