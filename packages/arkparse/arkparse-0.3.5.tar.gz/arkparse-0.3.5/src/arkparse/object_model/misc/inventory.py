import json
from dataclasses import dataclass
from uuid import UUID
from typing import Dict
from pathlib import Path

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing.struct import get_uuid_reference_bytes
from arkparse.logging import ArkSaveLogger

from .inventory_item import InventoryItem
from ...utils.json_utils import DefaultJsonEncoder


# items array InventoryItems -> ArrayProperty -> ObjectProperty

@dataclass
class Inventory(ParsedObjectBase):
    items: Dict[UUID, InventoryItem]
    started_empty: bool = False
    def __init__(self, uuid: UUID, save: AsaSave = None):
        super().__init__(uuid, save=save)
        self.items = {}

        if self.object is None:
            ArkSaveLogger.error_log(f"Inventory object with UUID {uuid} could not be loaded from save, not found")
            return

        item_arr = self.object.get_array_property_value("InventoryItems")
        for item in item_arr:
            item_uuid = UUID(item.value)
            item = InventoryItem(item_uuid, save=save)
            if item.object is None:
                ArkSaveLogger.warning_log(f"Inventory item {item_uuid} could not be loaded from save, not found")
            else:
                is_engram = item.object.get_property_value("bIsEngram")
                if is_engram is None or not is_engram:
                    self.items[item_uuid] = item

    @property
    def number_of_items(self):
        return len(self.items)

    def add_item(self, item: UUID, store: bool = True):
        if len(self.items) == 0:
            raise ValueError("Currently, adding stuff to empty inventories is not supported!")
            # self.binary.set_property_position("bInitializedMe")
        else:
            self.object.find_property("InventoryItems")

        self.items[item] = InventoryItem(item, self.save)
        self.items[item].add_self_to_inventory(self.object.uuid)

        object_references = []
        for item in self.items.keys():
            object_references.append(get_uuid_reference_bytes(item))

        if len(self.items) == 0:
            raise ValueError("Inventory cannot be empty when adding items (at this point in time)")
            # self.binary.insert_array("InventoryItems", "ObjectProperty", object_references)
        else:
            self.binary.set_property_position("InventoryItems")
            self.binary.replace_array("InventoryItems", "ObjectProperty", object_references)

        if store:
            self.update_binary()

    def remove_item(self, item: UUID):
        if len(self.items) == 0:
            return

        if item in self.items:
            self.items.pop(item)
        self.binary.set_property_position("InventoryItems")

        object_references = []
        for item in self.items:
            object_references.append(get_uuid_reference_bytes(item))

        self.binary.replace_array("InventoryItems", "ObjectProperty", object_references if len(object_references) > 0 else None)
        self.update_binary()

    def clear_items(self):
        if len(self.items) == 0:
            return

        self.items = []
        self.binary.set_property_position("InventoryItems")
        self.binary.replace_array("InventoryItems", "ObjectProperty", None)

        self.update_binary()

    def store_binary(self, path: Path, name: str = None, prefix: str = "inv_", with_content: bool = True, no_suffix: bool = False):
        super().store_binary(path, name=name, prefix=prefix, no_suffix=no_suffix)
        if not with_content:
            return
        for key, item in self.items.items():
            item.store_binary(path, prefix="itm_")

    def __str__(self):
        out = f"Inventory(items={len(self.items)}; uuid={self.object.uuid})"

        for _, item in self.items.items():
            out += "\n   - " + item.get_short_name() + f" ({item.object.uuid})"

        return out

    def to_json_obj(self):
        json_items = []
        for key, item in self.items.items():
            json_items.append(item.to_json_obj(include_owner_inv_uuid=False))
        return { "UUID": self.object.uuid.__str__(), "InventoryItems": json_items }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
