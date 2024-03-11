# This file is part of the DMComm project by BladeSabre. License: MIT.

# Source code for the RP2 PIO programs, to be pre-assembled using desktop Python.
# Main writes to ../lib/dmcomm/hardware/pio_programs.py .

import os
import adafruit_pioasm

# Output to pronged devices.
# Run with 1MHz clock, 2 set pins, initial_set_pin_direction=0 (input).
# First set pin is pin_drive_signal. Second set pin is pin_drive_low.
# PIO can change both values or directions at the same time. Change values before directions for output.
# If number sent is 0, drive the output low (both pins output low).
# If number sent is 1, drive the output high (pin_drive_signal output high, pin_drive_low output low).
# If number sent is 2, disable the output (both pins input).
# Otherwise, delay for approximately that number of microseconds.
prong_TX_ASM = """
start:
	pull
	mov x osr
	jmp x-- notdrivelow
	jmp drivelow  ; if osr==0
notdrivelow:
	jmp x-- notdrivehigh
	jmp drivehigh ; if osr==1
notdrivehigh:
	jmp x-- delay
	jmp release   ; if osr==2
	; else:
delay:
	jmp x-- delay
	jmp start
drivelow:
	set pins 0
	set pindirs 3
	jmp start
drivehigh:
	set pins 1
	set pindirs 3
	jmp start
release:
	set pindirs 0
"""

# Outputs the specified bytes to iC. Run with 100kHz clock.
# 1 out pin and 1 set pin which are the same.
iC_TX_ASM = """
	pull
	mov osr ~ osr
	set pins 1
	set pins 0 [7]
	set x 7
loop:
	out pins 1
	set pins 0 [7]
	jmp x-- loop
	nop [12]
"""

# Outputs the specified bytes to Xros Loader.
# Run with 583430 clock for trade/battle. Xroslink not currently supported.
# 1 out pin and 1 set pin which are the same.
xloader_TX_ASM = """
	pull
	mov osr ~ osr
	set pins 1 [4]
	set pins 0 [3]
	set x 7
loop:
	out pins 1
	set pins 0 [7]
	jmp x-- loop
	set x 24
delay_x:
	set y 31
delay_y:
	jmp y-- delay_y [1]
	jmp x-- delay_x
"""

this_file_name = os.path.basename(__file__)

output_text = f"""# This file is part of the DMComm project by BladeSabre. License: MIT.
# Auto-generated from {this_file_name} - do not edit.

from array import array

prong_TX = {repr(adafruit_pioasm.assemble(prong_TX_ASM))}

iC_TX = {repr(adafruit_pioasm.assemble(iC_TX_ASM))}

xloader_TX = {repr(adafruit_pioasm.assemble(xloader_TX_ASM))}
"""

if __name__ == "__main__":
	dir_above = os.path.dirname(os.path.dirname(os.path.realpath("__file__")))
	target_filepath = os.path.join(dir_above, "lib/dmcomm/hardware/pio_programs.py")
	with open(target_filepath, "w") as f:
		f.write(output_text)
