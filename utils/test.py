# This file is part of the DMComm project by BladeSabre. License: MIT.

# We can test protocol modules from CPython.

import dmcomm.protocol
from dmcomm.protocol import dm20

name1 = dm20.Name.from_english("BOB")
assert name1.name == "BOB "
assert name1.english_name == "BOB "
assert name1.japanese_name == "イソイ　"
assert name1[0] == 2
assert name1[1] == 15
assert name1[3] == 0

# Converted a real result to this DigiROM string.
digirom = dmcomm.protocol.parse_command("V2-2801-0001-320E-020E-162E-047E-025E-14EE-142E-90FE")
view = dm20.BattleOrCopyView(digirom)
assert view.name.japanese_name == "アリア　"
assert view.turn == 2
assert view.pattern == 12
assert view.mode == dm20.MODE_TAG
assert view.version == dm20.VERSION_TAICHI
assert view.index == 8 #Airdramon
assert view.attribute == dm20.ATTRIBUTE_VACCINE
assert view.sprite_strong == 5
assert view.sprite_weak == 34
assert view.power == 0x47
assert view.power_bonus == 16
assert view.index_rear == 9 #Seadramon
assert view.attribute_rear == dm20.ATTRIBUTE_DATA
assert view.sprite_strong_rear == 5
assert view.sprite_weak_rear == 14
assert view.power_rear == 0x42
assert view.power_bonus_rear == 16
assert view.tag_meter == 1 #2 arrows
assert view.hit_me == 0
assert view.hit_you == 15
assert view.checksum == 9

# Rebuild the above.
dm20cmd = dm20.BattleOrCopy(dm20.MODE_TAG, 2)
dm20cmd.name = dm20.Name.from_japanese("アリア　")
dm20cmd.pattern = 12
dm20cmd.version = dm20.VERSION_TAICHI
dm20cmd.index = 8 #Airdramon
dm20cmd.power = 0x47
dm20cmd.index_rear = 9 #Seadramon
dm20cmd.power_bonus_rear = 16 #trying it both ways
dm20cmd.tag_meter = 1
dm20cmd.hit_me = 0
assert dm20cmd[0].data == 0x2801
assert dm20cmd[1].data == 0x0001
assert dm20cmd[2].data == 0x320E
assert dm20cmd[3].data == 0x020E
assert dm20cmd[4].data == 0x162E
assert dm20cmd[5].data == 0x047E
assert dm20cmd[6].data == 0x025E
assert dm20cmd[7].data == 0x14EE
assert dm20cmd[8].data == 0x142E
#TODO dm20cmd[9].data == 0x00FE #check digit is done later

dm20cmd = dm20.BattleOrCopy(dm20.MODE_TAG, 1)
dm20cmd.version = dm20.VERSION_YAMATO
dm20cmd.name = name1
dm20cmd.pattern = 5
assert dm20cmd[0].data == 0x0F02
assert dm20cmd[1].data == 0x0002
assert dm20cmd[2].data == 0x961E
