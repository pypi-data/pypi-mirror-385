from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser
import random
from arkparse.logging import ArkSaveLogger

@dataclass
class ArkItemNetId:
    id1 : int
    id2 : int

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        if byte_buffer.peek_name() == "ItemID2":
            self.id1 = 0
        else:
            self.id1 = byte_buffer.parse_uint32_property("ItemID1")
        self.id2 = byte_buffer.parse_uint32_property("ItemID2")
        byte_buffer.validate_name("None")

        ArkSaveLogger.parser_log(f"ArkItemNetId: {self.id1}, {self.id2}")


    def replace(self, byte_buffer: "ArkBinaryParser", new_id1: int = None, new_id2: int = None):
        if new_id1 is None:
            new_id1 = random.randint(0, 2**31 - 1)
        if new_id2 is None:
            new_id2 = random.randint(0, 2**31 - 1)

        byte_buffer.set_property_position("ItemID1")
        byte_buffer.validate_name("ItemID1")
        byte_buffer.validate_name("UInt32Property")
        byte_buffer.validate_uint32(0)
        byte_buffer.validate_uint32(4)
        byte_buffer.validate_byte(0)
        byte_buffer.replace_bytes(new_id1.to_bytes(4, byteorder="little"))
        byte_buffer.validate_name("ItemID2")
        byte_buffer.validate_name("UInt32Property")
        byte_buffer.validate_uint32(0)
        byte_buffer.validate_uint32(4)
        byte_buffer.validate_byte(0)
        byte_buffer.replace_bytes(new_id2.to_bytes(4, byteorder="little"))
        byte_buffer.validate_name("None")

        self.id1 = new_id1
        self.id2 = new_id2

    def __str__(self):
        return f"ArkItemNetId: {self.id1}, {self.id2}"

    def to_json_obj(self):
        return { "ItemID1": self.id1, "ItemID2": self.id2 }
