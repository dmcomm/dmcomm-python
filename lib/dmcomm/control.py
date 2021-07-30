# This file is part of the DMComm project by BladeSabre. License: MIT.

class Controller:
	def __init__(self):
		pass
	def register(self, io_object):
		pass
	def execute(self, command):
		parts = command.strip().upper().split("-")
		if len(parts[0]) >= 2:
			op = parts[0][:-1]
			turn = parts[0][-1]
		else:
			op = parts[0]
			turn = ""
		if op == "D":
			raise NotImplementedError("debug")
		elif op == "T":
			raise NotImplementedError("test")
		elif op not in ["V", "X", "Y", "!DL", "!FL", "!IC"]:
			raise ValueError("op=" + op)
		elif turn not in "012":
			raise ValueError("turn=" + turn)

		return("...")
