# This file is part of the DMComm project by BladeSabre. License: MIT.
"""
`board_config.py`
=================

Handles differences between boards.

Currently we have recommended pin assignments for
Raspberry Pi Pico and Arduino Nano RP2040 Connect.
"""

import board
import dmcomm.hardware as hw

if board.board_id == "arduino_nano_rp2040_connect":
	controller_pins = [
		hw.ProngOutput(board.A0, board.A2),
		hw.ProngInput(board.A3),
		hw.InfraredOutput(board.D9),
		hw.InfraredInputModulated(board.D10),
		hw.InfraredInputRaw(board.D5),
		hw.TalisInputOutput(board.D4),
	]
	extra_power_pins = [
		(board.D6, False),
		(board.D7, True),
		(board.D8, False),
		(board.D11, False),
		(board.D12, True),
	]
elif board.board_id == "raspberry_pi_pico":
	controller_pins = [
		hw.ProngOutput(board.GP19, board.GP21),
		hw.ProngInput(board.GP26),
		hw.InfraredOutput(board.GP16),
		hw.InfraredInputModulated(board.GP17),
		hw.InfraredInputRaw(board.GP14),
		hw.TalisInputOutput(board.GP15),
	]
	extra_power_pins = [
		(board.GP11, True),
		(board.GP13, True),
		(board.GP18, True),
	]
else:
	raise ValueError("Please configure pins in board_config.py")
