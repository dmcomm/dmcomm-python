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
	op_turn = parts[0]
	try:
		turn = int(op_turn[-1])
		op = op_turn[:-1]
	except ValueError:
		turn = None
		op = op_turn
	except IndexError:
		raise CommandError("op=")
	if op in ["T", "I", "P"]:
		return OtherCommand(op)
	elif op in ["V", "X", "Y", "IC"]:
		DigiROM = digirom.ClassicDigiROM
	elif op in ["C"]:
		DigiROM = digirom.WordsDigiROM
	elif op in ["DL", "FL", "LT"]:
		DigiROM = digirom.BytesDigiROM
	elif op in ["BC"]:
		DigiROM = digirom.DigitsDigiROM
	else:
		raise CommandError("op=" + op)
	if turn not in [0, 1, 2]:
		raise CommandError("turn=" + str(turn))
	return DigiROM(op, turn, text_segments=parts[1:])

class OtherCommand:
	def __init__(self, op):
		self.signal_type = None
		self.op = op
