# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.dm20`
======================

Handling of DM20 high-level protocol.

Note: This API is still under development and may change at any time.
"""

import array

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

ROSTER_SIZE = 134

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

_ATTRIBUTES = array.array("B")
_a = _ATTRIBUTES.fromlist
_a([3,3,0,2,0,1,2,1,0,1,2,2,1,0,2,1,3,3,1,1,0,0,0,0,0,0,2,2,1,2,0,1,3,3,1,2,0,1,2,2,1,1,2,0,0])
_a([2,0,2,3,3,0,1,1,1,0,2,1,0,2,2,1,1,0,2,3,3,2,2,2,2,2,2,2,2,2,2,2,0,2,2,3,3,0,0,0,0,1,1,1,1])
_a([3,3,1,0,0,0,2,2,2,3,3,0,0,0,0,1,1,1,1,0,0,0,0,1,0,0,1,3,3,1,1,1,0,3,3,0,3,0,0,2,2,1,0,0])
_SPRITES_STRONG = array.array("B")
_a = _SPRITES_STRONG.fromlist
_a([0,0,1,4,3,3,6,6,5,5,15,2,7,8,41,37,0,0,1,4,3,3,6,6,5,9,15,10,7,14,33,12,0,0,1,4,3,3])
_a([6,6,5,11,15,12,7,13,29,28,0,0,1,4,3,3,6,6,5,11,15,12,7,13,2,12,0,0,1,4,3,3,6,6,5,11])
_a([15,12,7,13,37,39,25,25,31,12,12,30,26,26,5,12,17,18,18,16,24,20,16,6,20,0,0,6,26,6])
_a([45,26,0,12,42,1,3,2,38,1,3,26,45,13,13,36,38,31,5,45,40,14,13,3,13,16,3,37,45,12])
_SPRITES_WEAK = array.array("B")
_a = _SPRITES_WEAK.fromlist
_a([0,0,26,31,25,26,12,17,34,14,15,26,6,6,4,32,0,0,25,41,25,5,22,35,17,5,15,2,26,8,11,30,0,0])
_a([12,41,25,1,11,27,9,5,15,2,20,8,0,38,0,0,5,39,31,12,11,23,41,5,15,2,22,8,9,30,0,0,41,31,26])
_a([5,5,25,14,5,15,2,22,8,25,28,25,25,25,31,14,31,1,12,16,34,17,18,31,21,31,31,21,13,5,0,0,17])
_a([7,14,3,0,5,5,5,26,5,26,26,25,26,32,25,5,24,13,13,13,13,45,40,43,26,26,22,12,32,12,41,16])
_MIN_POWERS = array.array("B")
_a = _MIN_POWERS.fromlist
_a([0,0,18,10,75,70,65,60,55,50,40,126,118,107,188,176,0,0,18,10,75,70,65,60,55,50,40,126])
_a([118,107,169,188,0,0,18,10,75,70,65,60,55,50,40,126,118,107,176,169,0,0,18,10,75,70,65,60])
_a([55,50,40,126,118,107,188,176,0,0,18,10,75,70,65,60,55,50,40,126,118,107,188,176,0,0,34])
_a([90,155,210,34,90,155,210,0,0,34,80,143,199,80,143,199,0,0,27,80,135,199,27,80,135,199,25])
_a([83,135,199,25,77,135,199,0,0,27,90,143,210,0,0,27,80,143,210,238,238,238,238,238])
assert len(_ATTRIBUTES) == ROSTER_SIZE
assert len(_SPRITES_STRONG) == ROSTER_SIZE
assert len(_SPRITES_WEAK) == ROSTER_SIZE
assert len(_MIN_POWERS) == ROSTER_SIZE
def default_attribute(index):
	return _ATTRIBUTES[index]
def default_sprite_strong(index):
	return _SPRITES_STRONG[index]
def default_sprite_weak(index):
	return _SPRITES_WEAK[index]
def min_power(index):
	return _MIN_POWERS[index]

class Name:
	@classmethod
	def from_japanese(cls, name: str):
		return cls.from_string(name, True)
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
	def power_bonus(self):
		i = self.index
		if i < ROSTER_SIZE:
			return self.power - min_power(i)
		else:
			return 0
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
	def power_bonus_rear(self):
		i = self.index_rear
		if i < ROSTER_SIZE:
			return self.power_rear - min_power(i)
		else:
			return 0
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
	def __init__(self, mode, turn):
		self.mode = mode
		self.turn = turn
		self.name = None
		self.pattern = None
		self.version = None
		self.index = None
		self.attribute = None
		self.sprite_strong = None
		self.sprite_weak = None
		self.power = None
		self.power_bonus = None
		self.index_rear = None
		self.attribute_rear = None
		self.sprite_strong_rear = None
		self.sprite_weak_rear = None
		self.power_rear = None
		self.power_bonus_rear = None
		self.tag_meter = None
		self.hit_me = None
		self.hit_you = None
		self._digirom = None
		self.result = None
		#: The opponent's properties.
		self.opponent = None
	def _index_send(self, front):
		if front:
			index = self.index
			active = self.mode != MODE_GET
		else:
			index = self.index_rear
			active = self.mode == MODE_TAG
		if not active:
			return 0
		elif index is None:
			return 3
		else:
			return index
	def _attribute_send(self, front):
		if front:
			attribute = self.attribute
			active = self.mode in (MODE_SINGLE, MODE_TAG)
		else:
			attribute = self.attribute_rear
			active = self.mode == MODE_TAG
		if not active:
			return 0
		elif attribute is None:
			return default_attribute(self._index_send(front))
		else:
			return attribute
	def _index_attribute_bits(self, front):
		index = self._index_send(front)
		attribute = self._attribute_send(front)
		return (index << 6) | (attribute << 4) | 0xE
	def _sprite_send(self, strong, front):
		if front:
			sprite = self.sprite_strong if strong else self.sprite_weak
			active = self.mode in (MODE_SINGLE, MODE_TAG)
		else:
			sprite = self.sprite_strong_rear if strong else self.sprite_weak_rear
			active = self.mode == MODE_TAG
		if not active:
			return 0
		elif sprite is None:
			f_default = default_sprite_strong if strong else default_sprite_weak
			return f_default(self._index_send(front))
		else:
			return sprite
	def _sprite_bits(self, front):
		sprite_strong = self._sprite_send(True, front)
		sprite_weak = self._sprite_send(False, front)
		return (sprite_strong << 10) | (sprite_weak << 4) | 0xE
	def _tag_meter_send(self, front):
		if front or self.mode != MODE_TAG or self.tag_meter is None:
			return 0
		else:
			return self.tag_meter
	def _power_send(self, front):
		if front:
			power = self.power
			bonus = self.power_bonus
			active = self.mode in (MODE_SINGLE, MODE_TAG)
		else:
			power = self.power_rear
			bonus = self.power_bonus_rear
			active = self.mode == MODE_TAG
		if not active:
			return (0, 0)
		min_pow = min_power(self._index_send(front))
		if power is None and bonus is None:
			power2 = min_pow
			bonus2 = 0
		elif power is None: #bonus is not None
			power2 = min_pow + bonus
			bonus2 = bonus
		else: #power is not None
			power2 = power
			bonus2 = power - min_pow
		return (power2, bonus2)
	def _meter_power_bits(self, front):
		tag_meter = self._tag_meter_send(front)
		(power, bonus) = self._power_send(front)
		return (tag_meter << 12) | (power << 4) | 0xE
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
			bits = 0x0101 if self.name is None else (self.name[1] << 8) | self.name[0]
		elif i == 2:
			bits = 0x0101 if self.name is None else (self.name[3] << 8) | self.name[2]
		elif i == 3:
			orderbit = 1 if self.turn == 1 else 0
			pattern = 0 if self.pattern is None else self.pattern
			bits = (orderbit << 15) | (pattern << 10) | (self.mode << 8) | (self.version << 4) | 0xE
		elif i == 4:
			bits = self._index_attribute_bits(True)
		elif i == 5:
			bits = self._sprite_bits(True)
		elif i == 6:
			bits = self._meter_power_bits(True)
		elif i == 7:
			bits = self._index_attribute_bits(False)
		elif i == 8:
			bits = self._sprite_bits(False)
		elif i == 9:
			bits = self._meter_power_bits(False)
		elif i == 10:
			#...
			segment = CommandSegment(bits, copy_mask, invert_mask, checksum_target)
		else:
			return None
		if i != 10:
			segment = CommandSegment(bits)
		return segment
