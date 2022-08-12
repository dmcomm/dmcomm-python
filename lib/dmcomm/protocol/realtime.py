# This file is part of the DMComm project by BladeSabre. License: MIT.

"""
`dmcomm.protocol.realtime`
==========================

Experimental handling of real-time protocols.

Note: This API is still under development and may change at any time.
"""

import time
import dmcomm.protocol

STATUS_IDLE = 0
STATUS_WAIT = 1
STATUS_PUSH = 2

class RealTime:
	def __init__(self, execute_callback, send_callback, receive_callback, status_callback):
		self._execute_callback = execute_callback
		self._send_callback = send_callback
		self._receive_callback = receive_callback
		self._status_callback = status_callback
		self.time_start = None
	def execute(self, rom_str):
		digirom = dmcomm.protocol.parse_command(rom_str)
		self._execute_callback(digirom)
		self.result = digirom.result
	def send_message(self):
		self._send_callback(self.message())
	def receive_message(self):
		message = self._receive_callback()
		if message is None:
			return None
		if not self.matched(message):
			raise CommandError("Unexpected message type: " + str(message))
		return message
	def update_status(self, status):
		self._status_callback(status)

class RealTimeHost(RealTime):
	def loop(self):
		if self.time_start is None:
			self.update_status(STATUS_PUSH)
			self.execute(self.scan_str)
			if self.scan_successful():
				self.send_message()
				self.time_start = time.monotonic()
				self.update_status(STATUS_WAIT)
		elif time.monotonic() - self.time_start > self.wait_max:
			self.time_start = None
		else:
			self.update_status(STATUS_WAIT)
			message = self.receive_message()
			if message is not None:
				self.execute(message)
				self.time_start = None

class RealTimeGuest(RealTime):
	def loop(self):
		message = self.receive_message()
		if message is not None:
			if self.push:
				self.update_status(STATUS_PUSH)
			self.execute(message)
			self.update_status(STATUS_WAIT)
			if self.comm_successful():
				self.send_message()

class RealTimeHostTalis(RealTimeHost):
	@property
	def scan_str(self):
		return "LT0"
	def scan_successful(self):
		return len(self.result) == 2 and len(self.result[0].data) >= 20
	def message(self):
		return "LT1-" + str(self.result[0])[2:] + "-AA590003" * 3
	@property
	def wait_min(self):
		return 0
	@property
	def wait_max(self):
		return 2
	def matched(self, rom_str):
		return rom_str.startswith("LT1-")

class RealTimeGuestTalis(RealTimeGuest):
	def matched(self, rom_str):
		return rom_str.startswith("LT1-")
	@property
	def push(self):
		return False
	def comm_successful(self):
		return len(self.result) >= 4
	def message(self):
		return "LT1-" + str(self.result[1])[2:] + "-AA590003" * 3

class RealTimeHostPenXBattle(RealTimeHost):
	@property
	def scan_str(self):
		return "X2-0069-2169-8009"
	def scan_successful(self):
		return len(self.result) == 7 and self.result[6].data is not None
	def message(self):
		return "X2-{0}-{1}-{2}-@4^1^F9".format(
			str(self.result[0])[2:],
			str(self.result[2])[2:],
			str(self.result[4])[2:],
		)
	@property
	def wait_min(self):
		return 0
	@property
	def wait_max(self):
		return 7
	def matched(self, rom_str):
		return rom_str.startswith("X1-")

class RealTimeGuestPenXBattle(RealTimeGuest):
	def matched(self, rom_str):
		return rom_str.startswith("X2-")
	@property
	def push(self):
		return True
	def comm_successful(self):
		return len(self.result) == 9
	def message(self):
		return "X1-{0}-{1}-{2}-{3}".format(
			str(self.result[0])[2:],
			str(self.result[2])[2:],
			str(self.result[4])[2:],
			str(self.result[6])[2:],
		)
