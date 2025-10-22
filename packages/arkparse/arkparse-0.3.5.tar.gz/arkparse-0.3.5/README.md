# ArkParse: A Python Library for Reading and Modifying ARK Save Files

**ArkParse** is a Python library designed for **ARK: Survival Ascended** players, server administrators, and modders. This library enables you to read, analyze, and modify ARK save files with an intuitive API. With ArkParse, you can access detailed information about players, structures, equipment, dinosaurs, and more, enabling powerful tools for automation, analysis, and customization.

## Introduction
Hi everyone,

I originally created this package to manage a private ARK server I started with a few friends. What began as a small project quickly grew into something much bigger than I expected!

The foundation for this work was built on the awesome efforts of [Kakoen](https://github.com/Kakoen) and their contributors, whose Java-based save file property parsing tools were a fantastic starting point. You can check out their work here: [Kakoen's ark-sa-save-tools](https://github.com/Kakoen/ark-sa-save-tools). However, since I'm more comfortable with Python, I decided to start my own package and expand on it significantly.

The package has grown to a pretty expansive set of tools that can be used to retrieve nearly everything in the save files, in a simple object oriented way.

I mainly use this package for server management tasks. Some highlights include:

 - Automatically changing server passwords to control when players can log in.
 - A voting system to reveal dino and base locations.
 - Sending random stats of the server to the chat
 - Monitoring player activity like when people log off and on and such
 - Randomly spawning bases with random loot for my friends to raid; probably my favorite feature (and the most complicated)
If you're curious or want to explore the features yourself, you can find the project here: [ark-server-manager](https://github.com/VincentHenauGithub/ark-server-manager).

Hope you find it useful or inspiring or both! 😊

## Discord
If you use the library a lot or want to chat about functionalities, I made a discord for that, which you can join here: [discord](https://discord.gg/cStrkZVzFE).

## Disclaimer
I'm not a professional Python programmer, so if you come across anything that could be done better, please bear with me, or, feel free to contribute! 😉

Secondly, the package is not fully complete, with some elements missing, such as blueprints in the Classes section, formulas for calculating coordinates for other maps than Abberation, and more. However, I hope the package is designed in a way that makes it relatively easy for you to add your own needs to it.

Last, I've never made an open source package like this so if I'm doing something wrong or don't know some general rules of thumb, feel free to tell me!
I just hope it's usefull for someone!

---
## Features

- **Player API**: Retrieve player and tribe data, including inventory details.
- **Structure API**: Analyze and filter structures by location, owner, and other criteria, create heatmaps and more...
- **Equipment API**: Explore equipment, armor, and saddles. Retrieve blueprints or create and insert custom items.
- **Dino API**: Analyze dino data, generate heatmaps, find specific dinos, or track stats like mutations and levels.
- **Base API**: Export and import entire bases for custom scenarios.
- **Stackable API**: Simple API for parsing basic resources, ammo, structure items and such...
- **Json API**: Simple API for exporting data as JSON.
- **General Tools**: Create custom save file content or perform bulk modifications.

---
## Installation

Install via pip:

```bash
pip install arkparse
```

Or install locally on your PC so you can add modifications
First clone the repo and then run the following in repo directory:
```bash
pip install -e .
```
---

### 4. **Quickstart**

There are quite a few examples under the examples folder, organized by api. These should help you on your way for most of the package functionalities, some of them are listed below already.

#### a. **Player API: Retrieve Player and Inventory Information**

```python
from arkparse import AsaSave
from arkparse.enums import ArkMap
from arkparse.ftp.ark_ftp_client import ArkFtpClient
from arkparse.api.player_api import PlayerApi
from arkparse.object_model.misc.inventory import Inventory

player_api = PlayerApi('../../ftp_config.json', ArkMap.ABERRATION)
save = AsaSave(contents=ArkFtpClient.from_config('../../ftp_config.json', ArkMap.ABERRATION).download_save_file())

for player in player_api.players:
    inventory: Inventory = player_api.get_player_inventory(player, save)
    print(player)
    print(f"{player.name}'s inventory:")
    print(inventory)
    print("\n")
```

---

#### b. **Structure API: Analyze Structures and Generate Heatmaps**

Retrieve and filter structures by owner, location, or type. Generate heatmaps for visualization and analysis.

```python
from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse import AsaSave, Classes
from arkparse.api import StructureApi
from arkparse.ftp import ArkFtpClient
from arkparse.enums import ArkMap
from arkparse.object_model.structures import StructureWithInventory

# retrieve the save file (can also retrieve it from a local path)
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

structure_api = StructureApi(save)
owning_tribe = 0 # add the tribe id here (check the player api examples to see how to get the tribe id)

vaults: Dict[UUID, StructureWithInventory] = structure_api.get_by_class([Classes.structures.placed.utility.vault])
vaults_owned_by = [v for v in vaults.values() if v.owner.tribe_id == owning_tribe]

print(f"Vaults owned by tribe {owning_tribe}:")
for v in vaults_owned_by:
    print(v)
```

---

#### c. **Equipment API: Manage Equipment and Blueprints**

```python
from pathlib import Path
from uuid import UUID
from typing import Dict

from arkparse.object_model.equipment.weapon import Weapon
from arkparse.saves.asa_save import AsaSave
from arkparse.ftp.ark_ftp_client import ArkFtpClient, ArkMap
from arkparse.api.equipment_api import EquipmentApi
from arkparse.classes.equipment import Weapons

# Retrieve save file
save_path = ArkFtpClient.from_config(Path("../../ftp_config.json"), ArkMap.ABERRATION).download_save_file(Path.cwd())
save = AsaSave(save_path)

equipment_api = EquipmentApi(save)

# Get all longneck blueprints
weapons: Dict[UUID, Weapon] = equipment_api.get_filtered(
    EquipmentApi.Classes.WEAPON,
    classes=[Weapons.advanced.longneck],
    only_blueprints=True
)

highest_dmg_bp = max(weapons.values(), key=lambda x: x.damage)
print(f"Highest damage on longneck bp: {highest_dmg_bp.damage}")
```

---

#### d. **Dino API: Analyze and Find Dinosaurs**

```python
from pathlib import Path

from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap
from arkparse.saves.asa_save import AsaSave
from arkparse.object_model.dinos.tamed_dino import TamedDino

save_path = Path.cwd() / "Aberration_WP.ark"  # Replace with path to your save file
save = AsaSave(save_path)
dino_api = DinoApi(save)

dinos = dino_api.get_all_tamed()

if dinos is None:
    print("No tamed dinos found")
    exit()

most_mutations: TamedDino = None
for dino in dinos.values():
    dino: TamedDino = dino
    curr = 0 if most_mutations is None else most_mutations.stats.get_total_mutations()
    if most_mutations is None or (dino.stats.get_total_mutations() > curr):
        most_mutations = dino

print(f"The dino with the most mutations is a {most_mutations.get_short_name()} with {int(most_mutations.stats.get_total_mutations())} mutations")
print(f"Location: {most_mutations.location.as_map_coords(ArkMap.ABERRATION)}")
print(f"Level: {most_mutations.stats.current_level}")
print(f"Owner: {most_mutations.owner}")
```

---

#### e. **JSON API: Export parsed data as JSON**

```python
from pathlib import Path

from arkparse import AsaSave
from arkparse.api.json_api import JsonApi

save_path = Path.cwd() / "Ragnarok_WP.ark" # replace with path to your save file
save = AsaSave(save_path) # loads save file
json_api = JsonApi(save) # initializes the JSON API

json_api.export_items() # exports items to JSON
```

## Contributing

I welcome contributions! If you have updates to this library that you would like to share, feel free!

Special thanks go to [O-S Marin](https://github.com/K07H) for many contributions to the library!
Check out his Arkparse powered save visualizer, [ASI (Ark-Save-Inspector)](https://github.com/K07H/ASA-Save-Inspector) Spoiler alert: it's pretty awesome 😊 

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
## Feedback & Support

- **Issues or Feature Requests**: Open an issue on the repo!
- **Help**: If you need help for something specific, you can always messageme, I will try to help you out

## Donation

If you really really love this package you can [donate here](https://www.paypal.com/donate/?hosted_button_id=BV63CTDUW7PKQ)
There is no need, but I also won't say no 😊


