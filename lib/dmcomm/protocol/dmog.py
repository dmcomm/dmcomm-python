# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.dmog`
======================

Handling of DMOG high-level protocol.

Note: This API is still under development and may change at any time.
"""

import array
import random

from dmcomm.protocol.digirom import ClassicDigiROM, ClassicCommandSegment, ResultView

ROSTER_SIZE = 12
_WIN_CHANCES = array.array("B", [
	 8,  8,  2,  3,  2,  3,  2,  3,  7,  1,  1,  1,
	 8,  8,  2,  3,  2,  3,  2,  3,  7,  1,  1,  1,
	15, 15,  8, 11,  9, 11,  7, 11, 13,  3,  3,  3,
	13, 13,  5,  8,  5,  9,  5,  7, 11,  2,  2,  2,
	15, 15,  7, 11,  8, 11,  9, 11, 13,  3,  3,  3,
	13, 13,  5,  7,  5,  8,  5,  9, 11,  2,  2,  2,
	15, 15,  9, 11,  7, 11,  8, 11, 13,  3,  3,  3,
	13, 13,  5,  9,  5,  7,  5,  8, 11,  2,  2,  2,
	 9,  9,  3,  5,  3,  5,  3,  5,  8,  1,  1,  1,
	15, 15, 13, 14, 13, 14, 13, 14, 15,  8,  5,  5,
	15, 15, 13, 14, 13, 14, 13, 14, 15, 11,  8,  5,
	15, 15, 13, 14, 13, 14, 13, 14, 15, 11, 11,  8])
assert len(_WIN_CHANCES) == ROSTER_SIZE ** 2

def win_chance(me_index, you_index, me_boost, you_boost):
	if me_index < 3:
		me_index = 3
	if me_index > 0xE:
		me_index = 0xE
	if you_index < 3:
		you_index = 3
	if you_index > 0xE:
		you_index = 0xE
	y = me_index - 3
	x = you_index - 3
	chance = _WIN_CHANCES[y * ROSTER_SIZE + x] + me_boost - you_boost
	#TODO is the cap 0 or 1? 15 or 16?
	if chance < 0:
		chance = 0
	if chance > 16:
		chance = 16
	return chance

class BattleView:
	"""DMOG parser.

	:param target: A `ResultView`, or `ClassicDigiROM` (calculations will be ignored).
	"""
	def __init__(self, target):
		self._target = target
	def _d(self, i):
		return self._target[i - 1].data
	@property
	def boost(self):
		return (self._d(1) >> 4) & 0xF
	@property
	def index(self):
		return self._d(1) & 0xF
	@property
	def version(self):
		return (self._d(2) >> 4) & 0xF
	@property
	def win(self):
		win_bits = self._d(2) & 0xF
		return win_bits == 1

class Outcome:
	@classmethod
	def from_result(cls, result, turn):
		me = BattleView(ResultView(result, turn))
		you = BattleView(ResultView(result, 3 - turn))
		return cls(me, you)
	def __init__(self, me: BattleView, you: BattleView):
		self.me = me
		self.you = you
	@property
	def ready(self):
		try:
			x = self.me.version
			x = self.you.version
			return True
		except (IndexError, TypeError):
			return False

class Battle:
	def __init__(self, turn):
		self.signal_type = "V"
		self.turn = turn
		self.boost = None
		self.index = None
		self.version = None
		self.win = None
		self._digirom = None
		self.result = None
		self.outcome = None
	def _boost_send(self):
		return 0 if self.boost is None else self.boost
	def _index_send(self):
		return 3 if self.index is None else self.index
	def _version_send(self):
		return 0 if self.version is None else self.version
	def prepare(self):
		self._digirom = ClassicDigiROM("V", self.turn)
		self._digirom.prepare()
		self.result = self._digirom.result
		self.outcome = Outcome.from_result(self.result, self.turn)
	def send(self):
		i = len(self._digirom)
		segment = self[i]
		self._digirom.append(segment)
		return self._digirom.send()
	def receive(self, bits):
		self._digirom.receive(bits)
	def __getitem__(self, i):
		i += 1
		if i == 1:
			rhs = (self._boost_send() << 4) | self._index_send()
		elif i == 2:
			if self.win is not None:
				win = self.win
			elif self.turn == 2:
				win = not self.outcome.you.win
			else:
				oc = self.outcome
				#TODO option to ignore boosts? get win chance separately?
				chance = win_chance(oc.me.index, oc.you.index, oc.me.boost, oc.you.boost)
				roll = random.randint(0, 15)
				win = chance > roll
			win_bits = 1 if win else 2
			rhs = (self._version_send() << 4) | win_bits
		else:
		    return None
		bits = ((rhs ^ 0xff) << 8) | rhs
		return ClassicCommandSegment(bits)
