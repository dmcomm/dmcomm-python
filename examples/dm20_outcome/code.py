# This file is part of the DMComm project by BladeSabre. License: MIT.

import board
import time

from dmcomm import CommandError, ReceiveError
import dmcomm.hardware as hw
from dmcomm.protocol import dm20

controller = hw.Controller()
controller.register(hw.ProngOutput(board.GP19, board.GP21))
controller.register(hw.ProngInput(board.GP26))

digirom = dm20.BattleOrCopy(dm20.MODE_TAG, 2)
digirom.pattern = 10
digirom.index = 5 #Tyranomon
digirom.index_rear = 7 #Meramon

while True:
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
		print("Front index: ", digirom.outcome.you.index)
		print("Rear index: ", digirom.outcome.you.index_rear)
		digirom.outcome.run()
		print("Damage dealt to you: ", digirom.outcome.damage_you)
		if digirom.outcome.end == dm20.OUTCOME_WIN:
			print("You lose!")
		elif digirom.outcome.end == dm20.OUTCOME_LOSE:
			print("You win!")
		else:
			print("Draw!")
	seconds_passed = time.monotonic() - time_start
	if seconds_passed < 5:
		time.sleep(5 - seconds_passed)
