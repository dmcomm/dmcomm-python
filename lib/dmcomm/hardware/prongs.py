# This file is part of the DMComm project by BladeSabre. License: MIT.

import array
import digitalio
import pulseio
import rp2pio

from dmcomm import ReceiveError
from . import WAIT_REPLY
from . import misc
from . import pio_programs

class BaseProngCommunicator:
	def __init__(self, prong_output, prong_input):
		self._pin_drive_signal = prong_output.pin_drive_signal
		self._pin_weak_pull = prong_output.pin_weak_pull
		self._pin_input = prong_input.pin_input
		self._output_state_machine = None
		self._output_weak_pull = None
		self._input_pulses = None
		self._params = self.params_class()
		self._enabled = False
	def enable(self, signal_type):
		if self._enabled:
			if signal_type == self._params.signal_type:
				return
			self.disable()
		self._params.set_signal_type(signal_type)
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
		self._ouput_state_machine = None
		self._output_weak_pull = None
		self._input_pulses = None
		self._enabled = False

class ClassicParams:
	def __init__(self):
		self.set_signal_type("V")
	def set_signal_type(self, signal_type):
		if signal_type == "V":
			self.idle_state = True
			self.invert_bit_read = False
			self.pre_idle_send = 3000
			self.pre_active_min = 40000
			self.pre_active_send = 59000
			#self.pre_active_max? PulseIn only goes up to 65535
			self.start_idle_min = 1500
			self.start_idle_send = 2083
			self.start_idle_max = 2500
			self.start_active_min = 600
			self.start_active_send = 917
			self.start_active_max = 1400
			self.bit_idle_min = 700
			self.bit0_idle_send = 1000
			self.bit_idle_threshold = 1800
			self.bit1_idle_send = 2667
			self.bit_idle_max = 3400
			self.bit_active_min = 1000
			self.bit1_active_send = 1667
			self.bit0_active_send = 3167
			self.bit_active_max = 4000
			self.cooldown_send = 400
			self.reply_timeout_ms = 100
			self.packet_length_timeout_ms = 300
		elif signal_type == "X":
			self.idle_state = True
			self.invert_bit_read = False
			self.pre_idle_send = 3000
			self.pre_active_min = 40000
			self.pre_active_send = 60000
			#self.pre_active_max? PulseIn only goes up to 65535
			self.start_idle_min = 1500
			self.start_idle_send = 2200
			self.start_idle_max = 3500
			self.start_active_min = 1000
			self.start_active_send = 1600
			self.start_active_max = 2600
			self.bit_idle_min = 800
			self.bit0_idle_send = 1600
			self.bit_idle_threshold = 2600
			self.bit1_idle_send = 4000
			self.bit_idle_max = 5500
			self.bit_active_min = 1200
			self.bit1_active_send = 1600
			self.bit0_active_send = 4000
			self.bit_active_max = 5500
			self.cooldown_send = 400
			self.reply_timeout_ms = 200
			self.packet_length_timeout_ms = 300
		elif signal_type == "Y":
			self.idle_state = False
			self.invert_bit_read = True
			self.pre_idle_send = 5000
			self.pre_active_min = 30000
			self.pre_active_send = 40000
			#self.pre_active_max? PulseIn only goes up to 65535
			self.start_idle_min = 9000
			self.start_idle_send = 11000
			self.start_idle_max = 13000
			self.start_active_min = 4000
			self.start_active_send = 6000
			self.start_active_max = 8000
			self.bit_idle_min = 1000
			self.bit0_idle_send = 4000
			self.bit_idle_threshold = 3000
			self.bit1_idle_send = 1400
			self.bit_idle_max = 4600
			self.bit_active_min = 1200
			self.bit1_active_send = 4400
			self.bit0_active_send = 1600
			self.bit_active_max = 5000
			self.cooldown_send = 200
			self.reply_timeout_ms = 100
			self.packet_length_timeout_ms = 300
		else:
			raise ValueError("signal_type must be V/X/Y")
		self.signal_type = signal_type

class ClassicCommunicator(BaseProngCommunicator):
	params_class = ClassicParams
	def send(self, bits):
		if not self._enabled:
			raise RuntimeError("not enabled")
		if self._params.idle_state == True:
			DRIVE_ACTIVE = 0
			DRIVE_IDLE = 1
		else:
			DRIVE_ACTIVE = 1
			DRIVE_IDLE = 0
		RELEASE = 2
		array_to_send = array.array("L", [
			DRIVE_IDLE, self._params.pre_idle_send,
			DRIVE_ACTIVE, self._params.pre_active_send,
			DRIVE_IDLE, self._params.start_idle_send,
			DRIVE_ACTIVE, self._params.start_active_send,
		])
		for i in range(16):
			array_to_send.append(DRIVE_IDLE)
			if bits & 1:
				array_to_send.append(self._params.bit1_idle_send)
				array_to_send.append(DRIVE_ACTIVE)
				array_to_send.append(self._params.bit1_active_send)
			else:
				array_to_send.append(self._params.bit0_idle_send)
				array_to_send.append(DRIVE_ACTIVE)
				array_to_send.append(self._params.bit0_active_send)
			bits >>= 1
		array_to_send.append(DRIVE_IDLE)
		array_to_send.append(self._params.cooldown_send)
		array_to_send.append(RELEASE)
		self._output_state_machine.write(array_to_send)
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		pulses = self._input_pulses
		pulses.clear()
		pulses.resume()
		if timeout_ms == WAIT_REPLY:
			timeout_ms = self._params.reply_timeout_ms
		misc.wait_for_length_2(pulses, 35, timeout_ms, self._params.packet_length_timeout_ms)
		pulses.pause()
		if len(pulses) == pulses.maxlen:
			raise ReceiveError("buffer full")
		if len(pulses) == 0:
			return None
		ic_bug = False
		if len(pulses) < 35:
			if self._params.signal_type == "X" and len(pulses) == 34:
				ic_bug = True
			else:
				raise ReceiveError("incomplete: %d pulses" % len(pulses))
		t = pulses.popleft()
		if t < self._params.pre_active_min:
			raise ReceiveError("pre_active = %d" % t)
		t = pulses.popleft()
		if t < self._params.start_idle_min or t > self._params.start_idle_max:
			raise ReceiveError("start_idle = %d" % t)
		t = pulses.popleft()
		if t < self._params.start_active_min or t > self._params.start_active_max:
			raise ReceiveError("start_active = %d" % t)
		result = 0
		for i in range(16):
			t = pulses.popleft()
			if t < self._params.bit_idle_min or t > self._params.bit_idle_max:
				raise ReceiveError("bit_idle %d = %d" % (i + 1, t))
			result >>= 1
			if t > self._params.bit_idle_threshold:
				result |= 0x8000
			if ic_bug and i == 15:
				break
			t = pulses.popleft()
			if t < self._params.bit_active_min or t > self._params.bit_active_max:
				raise ReceiveError("bit_active %d = %d" % (i + 1, t))
		if self._params.invert_bit_read:
			result ^= 0xFFFF
		return result

class ColorParams:
	def __init__(self):
		self.set_signal_type("C")
	def set_signal_type(self, signal_type):
		if signal_type == "C":
			self.idle_state = True
			self.pre_idle_send = 1000
			self.pre_active_min = 65535
			self.pre_active_send = 150000
			#self.pre_active_max? PulseIn only goes up to 65535
			self.bit_idle_min = 200
			self.bit_idle_send = 500
			self.bit_idle_max = 700
			self.bit_active_min = 200
			self.bit1_active_send = 1500
			self.bit_active_threshold = 1000
			self.bit0_active_send = 500
			self.bit_active_max = 1700
			self.cooldown_send = 500
			self.reply_timeout_ms = 200
			self.packet_length_timeout_ms = 400
			self.pulses_expected = 257
		else:
			raise ValueError("signal_type must be C")
		self.signal_type = signal_type

class ColorCommunicator(BaseProngCommunicator):
	params_class = ColorParams
	def send(self, data):
		if not self._enabled:
			raise RuntimeError("not enabled")
		DRIVE_ACTIVE = 0
		DRIVE_IDLE = 1
		RELEASE = 2
		array_to_send = array.array("L", [
			DRIVE_IDLE, self._params.pre_idle_send,
			DRIVE_ACTIVE, self._params.pre_active_send,
		])
		for bits in data:
			for i in range(16):
				array_to_send.append(DRIVE_IDLE)
				array_to_send.append(self._params.bit_idle_send)
				array_to_send.append(DRIVE_ACTIVE)
				if bits & 1:
					array_to_send.append(self._params.bit1_active_send)
				else:
					array_to_send.append(self._params.bit0_active_send)
				bits >>= 1
		array_to_send.append(DRIVE_IDLE)
		array_to_send.append(self._params.cooldown_send)
		array_to_send.append(RELEASE)
		self._output_state_machine.write(array_to_send)
	def receive(self, timeout_ms):
		if not self._enabled:
			raise RuntimeError("not enabled")
		pulses = self._input_pulses
		pulses.clear()
		pulses.resume()
		if timeout_ms == WAIT_REPLY:
			timeout_ms = self._params.reply_timeout_ms
		misc.wait_for_length_2(pulses, self._params.pulses_expected, timeout_ms, self._params.packet_length_timeout_ms)
		pulses.pause()
		if len(pulses) == pulses.maxlen:
			raise ReceiveError("buffer full")
		if len(pulses) == 0:
			return []
		ic_bug = False
		if len(pulses) < self._params.pulses_expected:
			raise ReceiveError("incomplete: %d pulses" % len(pulses))
		t = pulses.popleft()
		if t < self._params.pre_active_min:
			raise ReceiveError("pre_active = %d" % t)
		pulses = self._input_pulses
		results = []
		bit_count = 0
		while len(pulses) > 0:
			result = 0
			for i in range(16):
				t = pulses.popleft()
				if t < self._params.bit_idle_min or t > self._params.bit_idle_max:
					raise ReceiveError("bit_idle %d = %d" % (bit_count + 1, t))
				t = pulses.popleft()
				if t < self._params.bit_active_min or t > self._params.bit_active_max:
					raise ReceiveError("bit_active %d = %d" % (bit_count + 1, t))
				result >>= 1
				if t > self._params.bit_active_threshold:
					result |= 0x8000
				bit_count += 1
			results.append(result)
		return results
