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

def _sequence_from_hex_string(text, grouplen):
	"""Creates a list of command data from one of the dash-separated parts of a text command.

	For Bytes|WordsCommandSegment.

	:param grouplen: The number of hex digits in each group.
	"""
	if len(text) < grouplen or len(text) % grouplen != 0:
		raise CommandError("bad length: " + text)
	data = []
	for i in range(0, len(text)-1, grouplen):
		digits = text[i:i+grouplen]
		if digits in ["++++", "____", "++", "+?", "__", ">>"]:
			item = digits
		else:
			try:
				item = int(digits, 16)
			except:
				raise CommandError("not a recognised instruction or hex number: " + digits)
		data.append(item)
	return data

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

class BaseResultSegment:
	"""Describes the result of one segment of the communication.

	:param sent: True if this represents data sent, False if data received.
	:param data: The data sent or received.
		If sent is False, can be `null_value` to indicate nothing was received before timeout.
	"""
	null_value = None  #: Subclasses can override.
	def __init__(self, sent: bool, data):
		self.sent = sent
		self.data = data
	def str_data(self):
		raise NotImplementedError("Subclasses must override str_data()")
	def __str__(self):
		"""Returns text formatted for the serial protocol."""
		if self.sent:
			return "s:" + self.str_data()
		elif self.data == self.null_value:
			return "t"
		else:
			return "r:" + self.str_data()

class BaseDigiROM:
	"""Base class for describing the communication and recording the results.

	Caller should provide `segments` or `text_segments` or neither, but not both.
	"""
	command_segment_class = None  #: Subclasses must override.
	result_segment_class = None   #: Subclasses must override.
	def __init__(self, signal_type:str, turn:int, segments=None, text_segments=None):
		self.signal_type = signal_type
		self.turn = turn
		self.result = None
		if segments is not None:
			self._segments = segments
		elif text_segments is not None:
			conv = self.command_segment_class.from_string
			self._segments = [conv(item) for item in text_segments]
		else:
			self._segments = []
	def append(self, c):
		self._segments.append(c)
	def prepare(self):
		self.result = Result(self.signal_type)
		self._command_index = 0
		self._data_received = None
	def _pre_send(self, segment):
		return segment.data
	def next(self):
		if self._command_index >= len(self._segments):
			return None
		segment = self._segments[self._command_index]
		self._command_index += 1
		data = self._pre_send(segment)
		self.result.append(self.result_segment_class(True, data))
		return data
	def store(self, data):
		self.result.append(self.result_segment_class(False, data))
		self._data_received = data
	def __len__(self):
		return len(self._segments)
	def __getitem__(self, i):
		return self._segments[i]

class BaseHighLevelDigiROM:
	"""Base class for DigiROM field mapping.
	"""
	signal_type = None    #: Subclasses must override.
	digirom_class = None  #: Subclasses must override.
	view_class = None     #: Subclasses must override.
	outcome_class = None  #: Subclasses must override.
	def prepare(self):
		"""Relies on member: turn.
		Creates members: _digirom, result, outcome.
		"""
		self._digirom = self.digirom_class(self.signal_type, self.turn)
		self._digirom.prepare()
		self.result = self._digirom.result
		me = self.view_class(ResultView(self.result, self.turn))
		you = self.view_class(ResultView(self.result, 3 - self.turn))
		self.outcome = self.outcome_class(me, you)
	def next(self):
		i = len(self._digirom)
		segment = self[i]
		if segment is not None:
			self._digirom.append(segment)
		return self._digirom.next()
	def store(self, data):
		self._digirom.store(data)

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

class ClassicResultSegment(BaseResultSegment):
	"""Describes the result of one segment of the communication for 16-bit protocols.
	"""
	def str_data(self):
		return "%04X" % self.data

class ClassicDigiROM(BaseDigiROM):
	"""Describes the communication for 16-bit protocols and records the results.
	"""
	command_segment_class = ClassicCommandSegment
	result_segment_class = ClassicResultSegment
	def prepare(self):
		super().prepare()
		self._checksum = 0
	def _pre_send(self, c):
		bits_received = self._data_received or 0
		bits = c.data
		bits &= ~c.copy_mask
		bits |= c.copy_mask & bits_received
		bits &= ~c.invert_mask
		bits |= c.invert_mask & ~bits_received
		if c.checksum_target is not None:
			bits &= ~(0xF << c.check_digit_LSB_pos)
		for i in range(4):
			self._checksum += bits >> (4 * i)
		self._checksum %= 16
		if c.checksum_target is not None:
			check_digit = (c.checksum_target - self._checksum) % 16
			bits |= check_digit << c.check_digit_LSB_pos
			self._checksum = c.checksum_target
		return bits

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

class DigitsResultSegment(BaseResultSegment):
	"""Describes the result of one segment of the communication for digit-sequence protocols.
	"""
	null_value = []
	def str_data(self):
		digits = ["%d" % n for n in self.data]
		return "".join(digits)

class DigitsDigiROM(BaseDigiROM):
	"""Describes the communication for digit-sequence protocols and records the results.
	"""
	command_segment_class = DigitsCommandSegment
	result_segment_class = DigitsResultSegment

class BytesCommandSegment:
	"""Describes how to carry out one segment of the communication for byte-sequence protocols.
	"""
	@classmethod
	def from_string(cls, text):
		"""Creates a `BytesCommandSegment` from one of the dash-separated parts of a text command.
		"""
		return cls(_sequence_from_hex_string(text, 2))
	def __init__(self, data):
		self.data = data
	#def __str__():

class BytesResultSegment(BaseResultSegment):
	"""Describes the result of one segment of the communication for byte-sequence protocols.
	"""
	null_value = []
	def str_data(self):
		hex_parts = ["%02X" % b for b in self.data]
		return "".join(hex_parts)

class BytesDigiROM(BaseDigiROM):
	"""Describes the communication for byte-sequence protocols and records the results.
	"""
	command_segment_class = BytesCommandSegment
	result_segment_class = BytesResultSegment
	def _pre_send(self, segment):
		data_to_send = []
		for i in range(len(segment.data)):
			item = segment.data[i]
			if item == "++":
				b = sum(data_to_send[:i]) % 0x100
			elif item == "+?":
				b = checksum_datalink(data_to_send[:i])
			elif item == "__":
				try:
					b = self._data_received[i]
				except:
					b = 0
			elif item == ">>":
				try:
					b = self._data_received[i-1]
				except:
					b = 0
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
		return cls(_sequence_from_hex_string(text, 4))
	def __init__(self, data):
		self.data = data
	#def __str__():

class WordsResultSegment(BaseResultSegment):
	"""Describes the result of one segment of the communication for word-sequence protocols.
	"""
	null_value = []
	def str_data(self):
		hex_parts = ["%04X" % b for b in self.data]
		return "".join(hex_parts)

class WordsDigiROM(BaseDigiROM):
	"""Describes the communication for word-sequence protocols and records the results.
	"""
	command_segment_class = WordsCommandSegment
	result_segment_class = WordsResultSegment
	def _pre_send(self, segment):
		data_to_send = []
		for i in range(len(segment.data)):
			item = segment.data[i]
			if item == "++++":
				w = sum(data_to_send[:i]) % 0x10000
			elif item == "____":
				try:
					w = self._data_received[i]
				except:
					w = 0
			else:
				w = item
			data_to_send.append(w)
		return data_to_send
