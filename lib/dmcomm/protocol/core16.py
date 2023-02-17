# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.core16`
========================

Handling of 16-bit low-level protocols.

Note: This API is still under development and may change at any time.
"""

from dmcomm import CommandError
from dmcomm.protocol import Result

class DigiROM:
	"""Describes the communication for 16-bit protocols and records the results.
	"""
	def __init__(self, signal_type, turn, segments=None):
		self.signal_type = signal_type
		self.turn = turn
		self._segments = [] if segments is None else segments
		self.result = None
	def append(self, c):
		self._segments.append(c)
	def prepare(self):
		self.result = Result(self.signal_type)
		self._command_index = 0
		self._bits_received = 0
		self._checksum = 0
	def send(self):
		if self._command_index >= len(self._segments):
			return None
		c = self._segments[self._command_index]
		self._command_index += 1
		bits = c.data
		bits &= ~c.copy_mask
		bits |= c.copy_mask & self._bits_received
		bits &= ~c.invert_mask
		bits |= c.invert_mask & ~self._bits_received
		if c.checksum_target is not None:
			bits &= ~(0xF << c.check_digit_LSB_pos)
		for i in range(4):
			self._checksum += bits >> (4 * i)
		self._checksum %= 16
		if c.checksum_target is not None:
			check_digit = (c.checksum_target - self._checksum) % 16
			bits |= check_digit << c.check_digit_LSB_pos
			self._checksum = c.checksum_target
		self.result.append(ResultSegment(True, bits))
		return bits
	def receive(self, bits):
		self.result.append(ResultSegment(False, bits))
		self._bits_received = bits
	def __len__(self):
		return len(self._segments)
	def __getitem__(self, i):
		return self._segments[i]

class CommandSegment:
	"""Describes how to carry out one segment of the communication for 16-bit protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `CommandSegment` from one of the dash-separated parts of a text command.
		"""
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
		return cls(bits, copy_mask, invert_mask, checksum_target, check_digit_LSB_pos)
	def __init__(self, bits, copy_mask=0, invert_mask=0, checksum_target=None, check_digit_LSB_pos=12):
		self.data = bits
		self.copy_mask = copy_mask
		self.invert_mask = invert_mask
		self.checksum_target = checksum_target
		self.check_digit_LSB_pos = check_digit_LSB_pos
	#def __str__():

class ResultSegment:
	"""Describes the result of one segment of the communication for 16-bit protocols.

	:param sent: True if this represents data sent, False if data received.
	:param data: A 16-bit integer representing the bits sent or received.
		If sent is False, can be None to indicate nothing was received before timeout.
	"""
	def __init__(self, sent: bool, data: int):
		self.sent = sent
		self.data = data
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		if self.sent:
			return "s:%04X" % self.data
		elif self.data is None:
			return "t"
		else:
			return "r:%04X" % self.data
