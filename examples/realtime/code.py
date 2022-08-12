# This file is part of the DMComm project by BladeSabre. License: MIT.

# Experimental real-time battles. PenX seems to be working, Talis not.

import board
import digitalio
import time

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
from dmcomm.protocol.realtime import *

message_from_host = None
message_from_guest = None

led_host = digitalio.DigitalInOut(board.LED)
led_host.switch_to_output()
controller_host = hw.Controller()
controller_host.register(hw.ProngOutput(board.GP19, board.GP21))
controller_host.register(hw.ProngInput(board.GP26))
controller_host.register(hw.TalisInputOutput(board.GP15))
def execute_callback_host(digirom):
	controller_host.execute(digirom)
	print("Host execute result:", digirom.result)
def send_callback_host(message):
	global message_from_host
	message_from_host = message
	print("Host sent message:", message)
def receive_callback_host():
	global message_from_guest
	if message_from_guest is not None:
		msg = message_from_guest
		message_from_guest = None
		return msg
def status_callback_host(status):
	led_host.value = status == STATUS_PUSH

led_guest = digitalio.DigitalInOut(board.GP5)
led_guest.switch_to_output()
controller_guest = hw.Controller()
controller_guest.register(hw.ProngOutput(board.GP6, board.GP9))
controller_guest.register(hw.ProngInput(board.GP8))
controller_guest.register(hw.TalisInputOutput(board.GP10))
def execute_callback_guest(digirom):
	controller_guest.execute(digirom)
	print("Guest execute result:", digirom.result)
def send_callback_guest(message):
	global message_from_guest
	message_from_guest = message
	print("Guest sent message:", message)
def receive_callback_guest():
	global message_from_host
	if message_from_host is not None:
		msg = message_from_host
		message_from_host = None
		return msg
def status_callback_guest(status):
	led_guest.value = status == STATUS_PUSH

rt_host = RealTimeHostPenXBattle(execute_callback_host, send_callback_host, receive_callback_host, status_callback_host)
rt_guest = RealTimeGuestPenXBattle(execute_callback_guest, send_callback_guest, receive_callback_guest, status_callback_guest)

while True:
	rt_host.loop()
	time.sleep(0.05)
	rt_guest.loop()
	time.sleep(0.05)
