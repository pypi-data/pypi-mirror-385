from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkRotator:
    pitch: float
    yaw: float
    roll: float

    def __init__(self, binary_data: "ArkBinaryParser" = None, from_struct: bool = False, yaw: float = 0.0, pitch: float = 0.0, roll: float = 0.0):
        if from_struct:
            binary_data.validate_name("StructProperty")
            binary_data.validate_uint32(1)
            binary_data.validate_name("Rotator")
            binary_data.validate_uint32(1)
            binary_data.validate_name("/Script/CoreUObject")
            binary_data.validate_uint32(0)
            binary_data.validate_uint32(0x18)
            binary_data.validate_byte(8)
            self.pitch = binary_data.read_double()
            self.yaw = binary_data.read_double()
            self.roll = binary_data.read_double()
        elif binary_data is not None:
            self.pitch = binary_data.read_double()
            self.yaw = binary_data.read_double()
            self.roll = binary_data.read_double()
        else:
            self.pitch = pitch
            self.yaw = yaw
            self.roll = roll

    def __str__(self):
        return f"Rotator(Pitch: {self.pitch:.2f}, Yaw: {self.yaw:.2f}, Roll: {self.roll:.2f})"

    def to_json_obj(self):
        return { "pitch": self.pitch, "yaw": self.yaw, "roll": self.roll }
