# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol`
=================

Protocol handling for Digimon toys.

Note: This API is still under development and may change at any time.

"""

from dmcomm import CommandError
from dmcomm.protocol import digirom

def parse_command(text):
	parts = text.strip().upper().split("-")
	if len(parts[0]) >= 2:
		op = parts[0][:-1]
		turn = parts[0][-1]
	else:
		op = parts[0]
		turn = ""
	if op in ["D", "T", "?"]:
		return OtherCommand(op, turn)
	elif op in ["V", "X", "Y", "IC"]:
		CommandSegment = digirom.ClassicCommandSegment
		DigiROM = digirom.ClassicDigiROM
	elif op in ["C"]:
		CommandSegment = digirom.WordsCommandSegment
		DigiROM = digirom.WordsDigiROM
	elif op in ["DL", "FL", "LT"]:
		CommandSegment = digirom.BytesCommandSegment
		DigiROM = digirom.BytesDigiROM
	elif op in ["BC"]:
		CommandSegment = digirom.DigitsCommandSegment
		DigiROM = digirom.DigitsDigiROM
	else:
		raise CommandError("op=" + op)
	if turn not in "012":
		raise CommandError("turn=" + turn)
	segments = [CommandSegment.from_string(part) for part in parts[1:]]
	return DigiROM(op, int(turn), segments)

class OtherCommand:
	def __init__(self, op, param):
		self.op = op
		self.param = param
