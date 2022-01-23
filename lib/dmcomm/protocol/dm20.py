# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.dm20`
======================

Handling of DM20 high-level protocol.

Note: This API is still under development and may change at any time.
"""

from dmcomm.protocol import ResultView
from dmcomm.protocol.core16 import DigiROM, CommandSegment

MODE_SINGLE = 0
MODE_SEND = 1
MODE_TAG = 2
MODE_GET = 3

VERSION_TAICHI = 0
VERSION_YAMATO = 1
VERSION_CORONA = 2
VERSION_LUNA = 3
VERSION_MEICOO = 4
VERSION_SILVER_BLACK = 6
VERSION_SILVER_BLUE = 7
VERSION_DUKE = 8
VERSION_BEELZE = 9

ATTRIBUTE_VACCINE = 0
ATTRIBUTE_DATA = 1
ATTRIBUTE_VIRUS = 2
ATTRIBUTE_FREE = 3

_CHARACTERS_ENGLISH = " ABCDEFGHIJKLMNOPQRSTUVWXYZ-!?"
_CHARACTERS_JAPANESE = ("　アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロ"
	"ワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポァィゥェォャュョッー！？")
def _make_reverse_lookup(characters):
	result = {}
	for i in range(len(characters)):
		result[characters[i]] = i
	return result
_LOOKUP_ENGLISH = _make_reverse_lookup(_CHARACTERS_ENGLISH)
_LOOKUP_JAPANESE = _make_reverse_lookup(_CHARACTERS_JAPANESE)
for (_wide, _ascii) in [("　", " "), ("ー", "-"), ("！", "!"), ("？", "?")]:
	_LOOKUP_JAPANESE[_ascii] = _LOOKUP_JAPANESE[_wide]

class Name:
	@classmethod
	def from_japanese(cls, name: str):
		return cls.from_string(cls, name, True)
	@classmethod
	def from_english(cls, name: str):
		return cls.from_string(name, False)
	@classmethod
	def from_string(cls, name: str, japanese: bool):
		if japanese:
			lookup = _LOOKUP_JAPANESE
		else:
			lookup = _LOOKUP_ENGLISH
		values = [0, 0, 0, 0]
		for i in range(min(len(name), 4)):
			values[i] = lookup.get(name[i], 0)
		return cls(values, japanese)
	def __init__(self, values, japanese: bool = True):
		self._values = values
		self.japanese = japanese
	def __getitem__(self, i: int):
		return self._values[i]
	@property
	def name(self):
		return self._name(self.japanese)
	@property
	def japanese_name(self):
		return self._name(True)
	@property
	def english_name(self):
		return self._name(False)
	def _name(self, japanese: bool):
		if japanese:
			characters = _CHARACTERS_JAPANESE
		else:
			characters = _CHARACTERS_ENGLISH
		result = []
		for i in range(4):
			v = self._values[i]
			if v > len(characters):
				v = 0
			result.append(characters[v])
		return "".join(result)

class BattleOrCopyView:
	"""DM20 parser.

	:param target: A `ResultView`, or `core16.DigiROM` (calculations will be ignored)."""
	def __init__(self, target):
		self._target = target
	def _d(self, i):
		return self._target[i - 1].data
	@property
	def name(self):
		data = [self._d(1) & 0xFF, self._d(1) >> 8, self._d(2) & 0xFF, self._d(2) >> 8]
		return Name(data)
	@property
	def turn(self):
		turn_bit = self._d(3) >> 15
		return 2 if turn_bit == 0 else 1
	@property
	def pattern(self):
		return (self._d(3) >> 10) & 0x1F
	@property
	def mode(self):
		return (self._d(3) >> 8) & 3
	@property
	def version(self):
		return (self._d(3) >> 4) & 0xF
	@property
	def index(self):
		return self._d(4) >> 6
	@property
	def attribute(self):
		return (self._d(4) >> 4) & 3
	@property
	def sprite_strong(self):
		return self._d(5) >> 10
	@property
	def sprite_weak(self):
		return (self._d(5) >> 4) & 0x3F
	@property
	def power(self):
		return (self._d(6) >> 4) & 0xFF
	@property
	def index_rear(self):
		return self._d(7) >> 6
	@property
	def attribute_rear(self):
		return (self._d(7) >> 4) & 3
	@property
	def sprite_strong_rear(self):
		return self._d(8) >> 10
	@property
	def sprite_weak_rear(self):
		return (self._d(8) >> 4) & 0x3F
	@property
	def power_rear(self):
		return (self._d(9) >> 4) & 0xFF
	@property
	def tag_meter(self):
		return self._d(9) >> 12
	@property
	def hit_me(self):
		return (self._d(10) >> 8) & 0xF
	@property
	def hit_you(self):
		return (self._d(10) >> 4) & 0xF
	@property
	def checksum(self):
		return self._d(10) >> 12

class BattleOrCopy:
	"""Adapts DM20 fields to DigiROM interface (under construction)."""
	def __init__(self, turn):
		self.turn = turn
		self.name = None
		self.pattern = None
		self.mode = None
		self.version = None
		self.index = None
		self.attribute = None
		self.sprite_strong = None
		self.sprite_weak = None
		self.power = None
		self.index_rear = None
		self.attribute_rear = None
		self.sprite_strong_rear = None
		self.sprite_weak_rear = None
		self.power_rear = None
		self.tag_meter = None
		self.hit_me = None
		self.hit_you = None
		self._digirom = None
		self.result = None
		#: The opponent's properties.
		self.opponent = None
	def prepare(self):
		self._digirom = DigiROM("V", turn)
		self._digirom.prepare()
		self.result = self._digirom.result
		self.opponent = BattleOrCopyView(ResultView(self.result, 3 - self._turn))
	def send(self):
		i = self._digirom._command_index #TODO make accessor
		segment = self[i]
		self._digirom.append(segment)
		return self._digirom.send()
	def receive(self, bits):
		self._digirom.receive(bits)
	def __getitem__(self, i):
		i += 1
		if i == 1:
			bits = 0 if self.name is None else (self.name[1] << 8) | self.name[0]
		elif i == 2:
			bits = 0 if self.name is None else (self.name[3] << 8) | self.name[2]
		elif i == 3:
			orderbit = 1 if self.turn == 1 else 0
			pattern = 0 if self.pattern is None else self.pattern
			bits = (orderbit << 15) | (pattern << 10) | (self.mode << 8) | (self.version << 4) | 0xE
		elif i == 4:
			pass
		elif i == 10:
			#...
			segment = CommandSegment(bits, copy_mask, invert_mask, checksum_target)
		else:
			return None
		if i != 10:
			segment = CommandSegment(bits)
		return segment
