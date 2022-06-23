# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.auto`
======================

Auto-responder / punchbag.

Note: This API is still under development and may change at any time.
"""

from dmcomm.protocol import ResultView
from dmcomm.protocol.core16 import DigiROM, CommandSegment

TYPE_DMOG = 0
TYPE_PEN_BATTLE = 1
TYPE_D3_EGG = 2

class AutoResponderVX:
	def __init__(self, physical):
		self.physical = physical
		self.turn = 2
		self.result = None
		self._rotation = -1
	def _add(self, items):
		for item in items:
			if type(item) is int:
				self._digirom.append(CommandSegment(item))
			else:
				self._digirom.append(CommandSegment.from_string(item))
	def prepare(self):
		self._digirom = DigiROM(self.physical, self.turn)
		self._digirom.prepare()
		self.result = self._digirom.result
		self._rview = ResultView(self.result, 1)
		self._type = None
		self._packet = -1
	def send(self):
		self._packet += 1
		if len(self._digirom) > self._packet:
			pass
		elif self._packet == 0:
			data = self._rview[0].data
			byteH = data >> 8
			byteL = data & 0xFF
			nibbleL = data & 0xF
			self._rotation += 1
			if byteH & byteL == 0:
				self._type = TYPE_DMOG
				self._add(["FB04", "F^30^3"])
			elif data & 0x0E0F == 0x000F:
				self._type = TYPE_PEN_BATTLE
				self._add(["204F", "000F",  "0^1^FF", "@BA7F"])
			elif data & 0xFF0F == 0x8C0F:
				self._type = TYPE_D3_EGG
				egg = self._rotation % 10
				egg_bits = 0x8C0F | (egg << 4)
				self._add([egg_bits, "@E80F"])
		return self._digirom.send()
	def receive(self, bits):
		self._digirom.receive(bits)
