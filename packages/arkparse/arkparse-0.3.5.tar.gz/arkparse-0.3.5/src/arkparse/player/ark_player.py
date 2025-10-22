import json
from pathlib import Path
from typing import List, Dict
from uuid import UUID

from arkparse.parsing import ArkPropertyContainer
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing.ark_archive import ArkArchive
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.object_model.misc.inventory import Inventory
from arkparse.object_model.misc.inventory import Inventory
from arkparse.object_model.ark_game_object import ArkGameObject

from .ark_persistent_buff_data import PersistentBuffData

from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing.struct import ArkVectorBoolPair, ArkTrackedActorIdCategoryPairWithBool, ArkMyPersistentBuffDatas

from .ark_character_config import ArkCharacterConfig
from .ark_character_stats import ArkCharacterStats
from ..utils.json_utils import DefaultJsonEncoder


class ArkPlayer:
    """
    Reads Ark: Survival Ascended *.arkprofile files
    """

    _archive: ArkArchive
    persistent_buffs : List[PersistentBuffData]
    location: ActorTransform = None
    inventory: Inventory

    name: str
    char_name: str
    tribe: int

    nr_of_deaths: int
    death_locations: List[ArkVectorBoolPair]

    waypoints: List[ArkTrackedActorIdCategoryPairWithBool]

    id_: int
    unique_id: str
    ip_address: str
    first_spawned: bool
    player_data_version: int

    last_time_died: float
    login_time: float

    config: ArkCharacterConfig
    stats: ArkCharacterStats

    persistent_buff_data = ArkMyPersistentBuffDatas

    def __init_player_data(self, props: ArkPropertyContainer):
        self.player_data_version = props.get_property_value("SavedPlayerDataVersion")

        my_data: ArkPropertyContainer = props.get_property_value("MyData")
        if not my_data:
            raise ValueError("Missing 'MyData' property.")
        
        self.id_ = my_data.get_property_value("PlayerDataID")
        self.char_name = my_data.get_property_value("PlayerCharacterName")
        self.unique_id = my_data.get_property_value("UniqueID").value if my_data.get_property_value("UniqueID") is not None else None
        self.ip_address = my_data.get_property_value("SavedNetworkAddress")
        self.name = my_data.get_property_value("PlayerName")
        self.first_spawned = my_data.get_property_value("bFirstSpawned")
        self.tribe = my_data.get_property_value("TribeID")
        self.last_time_died = my_data.get_property_value("LastTimeDiedToEnemyTeam")
        self.login_time = my_data.get_property_value("LoginTime")
        self.nr_of_deaths = my_data.get_property_value("NumOfDeaths", 0)

        deaths = my_data.get_array_property_value("ServerSavedLastDeathLocations")
        self.death_locations = []
        for death in deaths:
            self.death_locations.append(death)
        
        waypoints = my_data.get_array_property_value("SavedWaypointTrackedActorInfo")
        self.waypoints = []
        for waypoint in waypoints:
            self.waypoints.append(waypoint)

        self.persistent_buff_data = my_data.get_property_value("MyPersistentBuffDatas")

        self.config = ArkCharacterConfig(props)
        self.stats = ArkCharacterStats(props)
    
    def __init__(self, archive_data: bytes, from_store: bool):
        _archive = ArkArchive(archive_data, from_store)
        
        self.player_data = _archive.get_object_by_class("/Game/PrimalEarth/CoreBlueprints/PrimalPlayerDataBP.PrimalPlayerDataBP_C")
        
        if self.player_data is None:
            print(_archive.objects)
            raise ValueError("No PrimalPlayerDataBP found in archive.")
        
        self.__init_player_data(self.player_data)

        self.persistent_buffs = []
        for buff in _archive.get_all_objects_by_class("/Script/ShooterGame.PrimalBuffPersistentData"):
            self.persistent_buffs.append(PersistentBuffData(buff))

        self._archive = _archive
        self.inventory = {}

    def get_location_and_inventory(self, save: AsaSave, pawn: ArkGameObject, bypass_inventory: bool = False):
        self.location = ActorTransform(vector = pawn.get_property_value("SavedBaseWorldLocation"))
        inv_uuid = UUID(pawn.get_property_value("MyInventoryComponent").value)
        if not bypass_inventory:
            self.inventory = Inventory(inv_uuid, save=save)

    def __str__(self):
        return f"ArkPlayer: {self.char_name} (platform name=\'{self.name}\') in tribe {self.tribe} (ue5 id {self.unique_id}, ark id {self.id_})"

    def to_string_all(self):
        """
        Returns a comprehensive, compact string representation of ArkPlayerData.
        
        Returns:
            str: String representation of the ArkPlayerData instance.
        """
        parts = [
            "ArkPlayerData:",
            f"  Name: {self.name}",
            f"  Character Name: {self.char_name}",
            f"  Unreal engine ID: {self.unique_id}",
            f"  Tribe ID: {self.tribe}",
            f"  Number of Deaths: {self.nr_of_deaths}",
            f"  Death Locations: [{', '.join(str(dl) for dl in self.death_locations)}]",
            f"  Waypoints: [{', '.join(str(wp) for wp in self.waypoints)}]",
            f"  ID: {self.id_}",
            f"  IP Address: {self.ip_address}",
            f"  First Spawned: {self.first_spawned}",
            f"  Last Time Died: {self.last_time_died}",
            f"  Login Time: {self.login_time}",
            f"  Config: {self.config}",
            f"  Stats: {self.stats}"
        ]
        return "\n".join(parts)

    def to_json_obj(self):
        # Grab already set properties
        json_obj = { "SavedPlayerDataVersion": self.player_data_version,
                     "PlayerName": self.name,
                     "PlayerCharacterName": self.char_name,
                     "UniqueID": self.unique_id,
                     "TribeID": self.tribe,
                     "NumOfDeaths": self.nr_of_deaths,
                     "PlayerDataID": self.id_,
                     "SavedNetworkAddress": self.ip_address,
                     "bFirstSpawned": self.first_spawned,
                     "LastTimeDiedToEnemyTeam": self.last_time_died,
                     "LoginTime": self.login_time,
                     "Config": self.config.to_json_obj() if self.config is not None else None,
                     "Stats": self.stats.to_json_obj() if self.stats is not None else None,
                     "MyPersistentBuffDatas": self.persistent_buff_data.to_json_obj() if self.persistent_buff_data is not None else None,
                     "PrimalBuffPersistentData": self.persistent_buffs }

        # Grab location if it exists
        if self.location is not None:
            json_obj["ActorTransformX"] = self.location.x
            json_obj["ActorTransformY"] = self.location.y
            json_obj["ActorTransformZ"] = self.location.z

        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
