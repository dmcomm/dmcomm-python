# This file is part of the DMComm project by BladeSabre. License: MIT.

# Usage examples for the high-level DigiROM APIs.
# Enter a number on serial to select an option (console serial only).



import board
import time
import usb_cdc

import board_config
from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
from dmcomm.protocol import dm20, dmog



# Examples are here.

def dm20_tag_create_digirom():
	digirom = dm20.BattleOrCopy(dm20.MODE_TAG, 2)
	digirom.pattern = 10
	digirom.index = 5 #Tyranomon
	digirom.index_rear = 7 #Meramon
	return digirom

def dm20_tag_print_result(digirom):
	print("Your front index:", digirom.outcome.you.index)
	print("Your rear index:", digirom.outcome.you.index_rear)
	print("Your attack strengths:", digirom.outcome.you.attack_strengths)
	digirom.outcome.run()
	print("Damage dealt to you:", digirom.outcome.damage_you)
	if digirom.outcome.end == dm20.OUTCOME_WIN:
		print("You lose!")
	elif digirom.outcome.end == dm20.OUTCOME_LOSE:
		print("You win!")
	else:
		print("Draw!")

def dmog1_create_digirom():
	digirom = dmog.Battle(1)
	digirom.index = 7  # Devimon
	digirom.boost = 2
	return digirom

def dmog2_create_digirom():
	digirom = dmog.Battle(2)
	digirom.index = 7  # Devimon
	digirom.boost = 2
	return digirom

def dmog_print_result(digirom):
	print("Your index:", digirom.outcome.you.index)
	print("Your boost:", digirom.outcome.you.boost)
	print("Your version:", digirom.outcome.you.version)
	if digirom.outcome.you.win:
		print("You win!")
	else:
		print("You lose!")



controller = hw.Controller()
for pin_description in board_config.controller_pins:
	controller.register(pin_description)
serial = usb_cdc.console
serial.timeout = 0
options = [
	("DM20 tag battle (you go first: press button)", dm20_tag_create_digirom(), dm20_tag_print_result),
	("DMOG battle (you go first: press button)", dmog2_create_digirom(), dmog_print_result),
	("DMOG battle (you go second: wait)", dmog1_create_digirom(), dmog_print_result),
]
def print_options():
	for i in range(len(options)):
		print("[" + str(i) + "] ", options[i][0])
	print("(Single keypress without Enter)")
print_options()
digirom = None

while True:
	if serial.in_waiting != 0:
		digirom = None
		command = serial.read(100)
		try:
			option_number = int(command)
			(title, digirom, print_result) = options[option_number]
			print(title)
		except Exception as e:
			print(repr(command), ":", repr(e))
			print_options()
	if digirom is not None:
		time_start = time.monotonic()
		error = ""
		result_end = "\n"
		try:
			controller.execute(digirom)
		except (CommandError, ReceiveError) as e:
			error = repr(e)
			result_end = " "
		print(digirom.result, end=result_end)
		if error != "":
			print(error)
		if digirom.outcome.ready:
			print_result(digirom)
		seconds_passed = time.monotonic() - time_start
		if seconds_passed < 5:
			time.sleep(5 - seconds_passed)
