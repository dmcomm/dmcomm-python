# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.auto`
======================

Auto-responder / punchbag.

Note: This API is still under development and may change at any time.
"""

from dmcomm.protocol.digirom import ClassicDigiROM, ClassicCommandSegment, ResultView

TYPE_DMOG = 0
TYPE_PEN_BATTLE = 1
TYPE_D3_EGG = 2

TYPE_PENX_BATTLE = -1
TYPE_PENX_TRADE = -2

class AutoResponderVX:
	def __init__(self, signal_type):
		self.signal_type = signal_type
		self.turn = 2
		self.result = None
		self._rotation = -1
	def _add(self, items):
		for item in items:
			if type(item) is int:
				self._digirom.append(ClassicCommandSegment(item))
			else:
				self._digirom.append(ClassicCommandSegment.from_string(item))
	def prepare(self):
		self._digirom = ClassicDigiROM(self.signal_type, self.turn)
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
			if byteH ^ byteL == 0xFF:
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
			elif data & 0x0C0F == 0x0009:
				self._type = TYPE_PENX_BATTLE
				self._add(["0019", "3109", "C009", "@4^1^F9"])
			elif data & 0x0C0F == 0x0409:
				self._type = TYPE_PENX_TRADE
				item = (self._rotation % 13) + 3
				item_bits = 0x0409 | (item << 4)
				self._add([item_bits, "@2009"])
		return self._digirom.send()
	def receive(self, bits):
		self._digirom.receive(bits)
