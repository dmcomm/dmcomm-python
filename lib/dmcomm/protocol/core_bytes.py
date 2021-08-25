# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.core_bytes`
============================

Handling of byte-sequence low-level protocols.

Note: This API is still under development and may change at any time.
"""

from dmcomm import CommandError
from dmcomm.protocol import Result

class DigiROM:
	"""Describes the communication for byte-sequence protocols and records the results.
	"""
	def __init__(self, physical, turn, segments=[]):
		self.physical = physical
		self.turn = turn
		self._segments = segments
		self.result = None
	def append(self, c):
		self._segments.append(c)
	def prepare(self):
		self.result = Result(self.physical, 0)
		self._command_index = 0
	def send(self):
		if self._command_index >= len(self._segments):
			return None
		c = self._segments[self._command_index]
		self._command_index += 1
		self.result.append(ResultSegment(True, c.data))
		return c.data
	def receive(self, data):
		self.result.append(ResultSegment(False, data))
	def __len__(self):
		return len(self._segments)

class CommandSegment:
	"""Describes how to carry out one segment of the communication for byte-sequence protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `CommandSegment` from one of the dash-separated parts of a text command.
		"""
		if len(text) < 2 or len(text) % 2 != 0:
			raise CommandError("bad length: " + text)
		data = []
		for i in range(len(text)-2, -1, -2):
			digits = text[i:i+2]
			try:
				b = int(digits, 16)
			except:
				raise CommandError("not hex number: " + digits)
			data.append(b)
		return cls(data)
	def __init__(self, data):
		self.data = data
	#def __str__():

class ResultSegment:
	"""Describes the result of one segment of the communication for byte-sequence protocols.

	:param is_send: True if this represents data sent, False if data received.
	:param data: A list of 8-bit integers representing the bytes sent or received.
		If is_send is False, can be empty to indicate nothing was received before timeout.
	"""
	def __init__(self, is_send: bool, data: list):
		self.is_send = is_send
		self.data = data
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		hex_parts = ["%02X" % b for b in self.data]
		hex_parts.reverse()
		hex_str = "".join(hex_parts)
		if self.is_send:
			return "s:" + hex_str
		elif self.data == []:
			return "t"
		else:
			return "r:" + hex_str
