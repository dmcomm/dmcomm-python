# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.digirom`
==========================

Handling of DigiROM formats.

Note: This API is still under development and may change at any time.
"""

from dmcomm import CommandError

def checksum_datalink(bytes_):
	checksum = 0
	carry_bit = 0
	for item in bytes_:
		checksum += item + carry_bit
		if checksum >= 0x100:
			checksum &= 0xFF
			carry_bit = 1
		else:
			carry_bit = 0
	return checksum

class Result:
	"""Describes the result of the communication.
	"""
	def __init__(self, signal_type):
		self.signal_type = signal_type
		self._results = []
	def append(self, segment):
		self._results.append(segment)
	def __len__(self):
		return len(self._results)
	def __getitem__(self, i):
		return self._results[i]
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		return " ".join([str(r) for r in self._results])

class ResultView:
	"""Describes the result of one side of the communication.

	:param result: The Result to view.
	:param turn: 1 for the side who went first, 2 for the side who went second.
	"""
	def __init__(self, result, turn):
		self._result = result
		self._turn = turn
		if turn == 2:
			self._turn_index = 1
		else:
			self._turn_index = 0
	def __getitem__(self, i):
		return self._result[2 * i + self._turn_index]

class BaseDigiROM:
	"""Base class for describing the communication and recording the results.
	"""
	def __init__(self, result_segment_class, signal_type, turn, segments=None):
		self.result_segment_class = result_segment_class
		self.signal_type = signal_type
		self.turn = turn
		self._segments = [] if segments is None else segments
		self.result = None
	def append(self, c):
		self._segments.append(c)
	def prepare(self):
		self.result = Result(self.signal_type)
		self._command_index = 0
		self._data_received = None
	def _pre_send(self, data):
		return data
	def send(self):
		if self._command_index >= len(self._segments):
			return None
		data = self._segments[self._command_index].data
		self._command_index += 1
		data = self._pre_send(data)
		self.result.append(self.result_segment_class(True, data))
		return data
	def receive(self, data):
		self.result.append(self.result_segment_class(False, data))
		self._data_received = data
	def __len__(self):
		return len(self._segments)
	def __getitem__(self, i):
		return self._segments[i]

class ClassicCommandSegment:
	"""Describes how to carry out one segment of the communication for 16-bit protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `ClassicCommandSegment` from one of the dash-separated parts of a text command.
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

class ClassicResultSegment:
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

class ClassicDigiROM:
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
		self.result.append(ClassicResultSegment(True, bits))
		return bits
	def receive(self, bits):
		self.result.append(ClassicResultSegment(False, bits))
		self._bits_received = bits
	def __len__(self):
		return len(self._segments)
	def __getitem__(self, i):
		return self._segments[i]

class DigitsCommandSegment:
	"""Describes how to carry out one segment of the communication for digit-sequence protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `DigitsCommandSegment` from one of the dash-separated parts of a text command.
		"""
		data = []
		for digit in text:
			try:
				n = int(digit)
			except:
				raise CommandError("not a number: " + digit)
			data.append(n)
		return cls(data)
	def __init__(self, data):
		self.data = data
	#def __str__():

class DigitsResultSegment:
	"""Describes the result of one segment of the communication for digit-sequence protocols.

	:param sent: True if this represents data sent, False if data received.
	:param data: A list of integers representing the digits sent or received.
		If sent is False, can be empty to indicate nothing was received before timeout.
	"""
	def __init__(self, sent: bool, data: list):
		self.sent = sent
		self.data = data
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		digits = ["%d" % n for n in self.data]
		digit_str = "".join(digits)
		if self.sent:
			return "s:" + digit_str
		elif self.data == []:
			return "t"
		else:
			return "r:" + digit_str

class DigitsDigiROM(BaseDigiROM):
	"""Describes the communication for digit-sequence protocols and records the results.
	"""
	def __init__(self, signal_type, turn, segments=None):
		super().__init__(DigitsResultSegment, signal_type, turn, segments)

class BytesCommandSegment:
	"""Describes how to carry out one segment of the communication for byte-sequence protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `BytesCommandSegment` from one of the dash-separated parts of a text command.
		"""
		if len(text) < 2 or len(text) % 2 != 0:
			raise CommandError("bad length: " + text)
		data = []
		for i in range(0, len(text)-1, 2):
			digits = text[i:i+2]
			if digits in ["+?"]:
				b = digits
			else:
				try:
					b = int(digits, 16)
				except:
					raise CommandError("not hex number: " + digits)
			data.append(b)
		return cls(data)
	def __init__(self, data):
		self.data = data
	#def __str__():

class BytesResultSegment:
	"""Describes the result of one segment of the communication for byte-sequence protocols.

	:param sent: True if this represents data sent, False if data received.
	:param data: A list of 8-bit integers representing the bytes sent or received.
		If sent is False, can be empty to indicate nothing was received before timeout.
	"""
	def __init__(self, sent: bool, data: list):
		self.sent = sent
		self.data = data
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		hex_parts = ["%02X" % b for b in self.data]
		hex_str = "".join(hex_parts)
		if self.sent:
			return "s:" + hex_str
		elif self.data == []:
			return "t"
		else:
			return "r:" + hex_str

class BytesDigiROM(BaseDigiROM):
	"""Describes the communication for byte-sequence protocols and records the results.
	"""
	def __init__(self, signal_type, turn, segments=None):
		super().__init__(BytesResultSegment, signal_type, turn, segments)
	def _pre_send(self, data):
		data_to_send = []
		for i in range(len(data)):
			item = data[i]
			if item == "+?":
				b = checksum_datalink(data_to_send[:i])
			else:
				b = item
			data_to_send.append(b)
		return data_to_send

class WordsCommandSegment:
	"""Describes how to carry out one segment of the communication for word-sequence protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `WordsCommandSegment` from one of the dash-separated parts of a text command.
		"""
		if len(text) < 4 or len(text) % 4 != 0:
			raise CommandError("bad length: " + text)
		data = []
		for i in range(0, len(text)-1, 4):
			digits = text[i:i+4]
			try:
				b = int(digits, 16)
			except:
				raise CommandError("not hex number: " + digits)
			data.append(b)
		return cls(data)
	def __init__(self, data):
		self.data = data
	#def __str__():

class WordsResultSegment:
	"""Describes the result of one segment of the communication for word-sequence protocols.

	:param sent: True if this represents data sent, False if data received.
	:param data: A list of 16-bit integers representing the bytes sent or received.
		If sent is False, can be empty to indicate nothing was received before timeout.
	"""
	def __init__(self, sent: bool, data: list):
		self.sent = sent
		self.data = data
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		hex_parts = ["%04X" % b for b in self.data]
		hex_str = "".join(hex_parts)
		if self.sent:
			return "s:" + hex_str
		elif self.data == []:
			return "t"
		else:
			return "r:" + hex_str

class WordsDigiROM(BaseDigiROM):
	"""Describes the communication for word-sequence protocols and records the results.
	"""
	def __init__(self, signal_type, turn, segments=None):
		super().__init__(WordsResultSegment, signal_type, turn, segments)
