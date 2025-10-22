#TamedTimeStamp
import json
from uuid import UUID
from typing import TYPE_CHECKING, Optional, List
from pathlib import Path

from arkparse.object_model.dinos.dino_id import DinoId
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.dino_owner import DinoOwner
from arkparse.object_model.misc.inventory import Inventory
from arkparse.object_model.dinos.dino import Dino
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing.struct.object_reference import ObjectReference
from arkparse.parsing import ActorTransform
from arkparse.parsing.struct.ark_dino_ancestor_entry import ArkDinoAncestorEntry

from arkparse.utils.json_utils import DefaultJsonEncoder

if TYPE_CHECKING:
    from arkparse.object_model.cryopods.cryopod import Cryopod

class TamedDino(Dino):
    owner: DinoOwner
    inv_uuid: UUID
    _inventory: Inventory
    tamed_name: str
    percentage_imprinted: float
    cryopod: "Cryopod"

    @property
    def percentage_imprinted(self):
        return self.stats._percentage_imprinted
    
    @property
    def location(self) -> ActorTransform:
        if self.cryopod is not None and self._location.in_cryopod:
            container = self.save.get_container_of_inventory(self.cryopod.owner_inv_uuid)
            if container is not None:
                self._location = container.location
                self._location.in_cryopod = True

        return self._location
    
    def __init_props__(self):
        self._inventory = None
        super().__init_props__()

        self.cryopod = None
        self.tamed_name = self.object.get_property_value("TamedName")
        inv_uuid: ObjectReference = self.object.get_property_value("MyInventoryComponent")
        self.owner = DinoOwner(self.object)

        if inv_uuid is None:
            self.inv_uuid = None
            self._inventory = None
        else:
            self.inv_uuid = UUID(inv_uuid.value)

    def __init__(self, uuid: UUID = None, save: AsaSave = None, bypass_inventory: bool = True):
        self.inv_uuid = None
        self._inventory = None
        super().__init__(uuid, save=save)

        if self.inv_uuid is not None and not bypass_inventory:
            self._inventory = Inventory(self.inv_uuid, save=save)

    @property
    def inventory(self) -> Inventory:
        if self._inventory is None and self.inv_uuid is not None:
            self._inventory = Inventory(self.inv_uuid, save=self.save)
        return self._inventory

    def __str__(self) -> str:
        return "Dino(type={}, lv={}, owner={})".format(self.get_short_name(), self.stats.current_level, str(self.owner.tribe))
    
    def is_ancestor_of(self, other: "TamedDino") -> bool:
        if other is None or other.object is None or self.object is None:
            return False

        ancestors: List[ArkDinoAncestorEntry] = other.object.get_property_value("DinoAncestors", [])
        ancestors_m: List[ArkDinoAncestorEntry] = other.object.get_property_value("DinoAncestorsMale", [])

        for anc in ancestors:
            if anc.female.id_ == self.id_ or anc.male.id_ == self.id_:
                return True
        for anc in ancestors_m:
            if anc.female.id_ == self.id_ or anc.male.id_ == self.id_:
                return True
            
        return False
    
    @property
    def generation(self) -> int:
        ancestors: List[ArkDinoAncestorEntry] = self.object.get_property_value("DinoAncestors", [])
        ancestors_m: List[ArkDinoAncestorEntry] = self.object.get_property_value("DinoAncestorsMale", [])
        return max(len(ancestors), len(ancestors_m)) + 1
    
    @property
    def ancestor_ids(self) -> set[DinoId]:
        if self.object is None:
            return []
        ancestors: List[ArkDinoAncestorEntry] = self.object.get_property_value("DinoAncestors", [])
        ancestors_m: List[ArkDinoAncestorEntry] = self.object.get_property_value("DinoAncestorsMale", [])
        ids = set()
        for anc in ancestors:
            ids.add(anc.female.id_)
            ids.add(anc.male.id_)
        for anc in ancestors_m:
            ids.add(anc.female.id_)
            ids.add(anc.male.id_)
        return ids

    @staticmethod
    def from_object(dino_obj: ArkGameObject, status_obj: ArkGameObject, cryopod: "Cryopod" = None):
        d: TamedDino = TamedDino()
        d.object = dino_obj
        d.__init_props__()

        d.cryopod = cryopod
        Dino.from_object(dino_obj, status_obj, d)

        return d
    
    def remove_from_save(self):
        if self.inventory is not None:
            for item in list(self.inventory.items.keys()):
                self.save.remove_obj_from_db(item)
            self.save.remove_obj_from_db(self.inv_uuid)
        super().remove_from_save()

    def store_binary(self, path: Path, name = None, prefix = "obj_", no_suffix=False, force_inventory=False):
        if self.inventory is None and force_inventory:
            raise ValueError("Cannot store TamedDino without inventory.")
        print(self.inventory)
        if self.inventory is not None:
            self.inventory.store_binary(path, name, no_suffix=no_suffix)
        print(f"Storing TamedDino {self.object.uuid} at {path}")
        return super().store_binary(path, name, prefix, no_suffix)

    def to_json_obj(self):
        json_obj = super().to_json_obj()
        if self.cryopod is not None and self.cryopod.object is not None and self.cryopod.object.uuid is not None:
            json_obj["CryopodUUID"] = self.cryopod.object.uuid.__str__()
        return json_obj
    
    def set_owner(self, owner: DinoOwner):
        self.owner.replace_with(owner, self.binary)
        self.update_binary()

    def set_name(self, name: str):
        if self.tamed_name is not None:
            self.binary.replace_string(self.object.find_property("TamedName"), name)
            self.tamed_name = name
            self.update_binary()
            self.update_object()

    def add_item(self, item: UUID):        
        if self.inventory is None:
            raise ValueError("Cannot add item to TamedDino without inventory!")
        self.inventory.add_item(item)
        return True
    
    def remove_item(self, item: UUID):
        self.inventory.remove_item(item)
        self.update_binary()
        self.save.remove_obj_from_db(item)

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
