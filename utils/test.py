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
assert view.index_rear == 9 #Seadramon
assert view.attribute_rear == dm20.ATTRIBUTE_DATA
assert view.sprite_strong_rear == 5
assert view.sprite_weak_rear == 14
assert view.power_rear == 0x42
assert view.tag_meter == 1 #2 arrows
assert view.hit_me == 0
assert view.hit_you == 15
assert view.checksum == 9

dm20cmd = dm20.BattleOrCopy(1)
dm20cmd.mode = dm20.MODE_TAG
dm20cmd.version = dm20.VERSION_YAMATO
dm20cmd.name = name1
dm20cmd.pattern = 5
assert dm20cmd[0].data == 0x0F02
assert dm20cmd[1].data == 0x0002
assert dm20cmd[2].data == 0x961E
