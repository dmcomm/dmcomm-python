# This file is part of the DMComm project by BladeSabre. License: MIT.

from dmcomm import CommandError

class Encoder16:
	def __init__(self, communicator):
		self._communicator = communicator
		self.reset()
	def reset(self):
		self._bits_received = 0
		self._checksum = 0
	def send_bits(self, bits, copy_mask=0, invert_mask=0, checksum_target=None, check_digit_LSB_pos=12):
		bits &= ~copy_mask
		bits |= copy_mask & self._bits_received
		bits &= ~invert_mask
		bits |= invert_mask & ~self._bits_received
		if checksum_target is not None:
			bits &= ~(0xF << check_digit_LSB_pos)
		for i in range(4):
			self._checksum += bits >> (4 * i)
		self._checksum %= 16
		if checksum_target is not None:
			check_digit = (checksum_target - self._checksum) % 16
			bits |= check_digit << check_digit_LSB_pos
			self._checksum = checksum_target
		self._communicator.send(bits)
		return (bits, "s:%04X" % bits)
	def send_hex(self, text):
		bits = 0
		copy_mask = 0
		invert_mask = 0
		checksum_target = None
		check_digit_LSB_pos = None
		cursor = 0
		for i in range(4):
			LSB_pos = 12 - (i * 4)
			bits <<= 4
			try:
				ch1 = text[cursor]
				if ch1 == "@" or ch1 == "^":
					cursor += 1
					ch_digit = text[cursor]
				else:
					ch_digit = ch1
			except IndexError:
				raise CommandError("incomplete: " + text)
			try:
				digit = int(ch_digit, 16)
			except:
				raise CommandError("not hex number: " + ch_digit)
			if ch1 == "@":
				checksum_target = digit
				check_digit_LSB_pos = LSB_pos
			elif ch1 == "^":
				copy_mask |= (~digit & 0xF) << LSB_pos
				invert_mask |= digit << LSB_pos
			else:
				bits |= digit
			cursor += 1
		if cursor != len(text):
			raise CommandError("too long: " + text)
		return self.send_bits(bits, copy_mask, invert_mask, checksum_target, check_digit_LSB_pos)
	def receive(self, timeout_ms):
		data = self._communicator.receive(timeout_ms)
		if data is None:
			desc = "t"
		else:
			self._bits_received = data
			desc = "r:%04X" % data
		return (data, desc)
