import struct
from collections import namedtuple

HEADER = struct.Struct("II")

header_fields = ['opcode', 'timestamp']

# Character movement
CHAR_MOVE_STRUCT = struct.Struct(
    "QffffBb")
CharacterMovement = namedtuple(
    "CharacterMovement",
    header_fields + [
        "character_id",
        "velocity_x", "velocity_y",
        "viewport_x", "viewport_y",
        "jump", "rotation"])


class OPCODES:

    CHAR_MOVE = 0x30

_opcode_map = {
    OPCODES.CHAR_MOVE: (CHAR_MOVE_STRUCT, CharacterMovement),
}


def parse(self, packet, opcode_map=_opcode_map):
    header = HEADER.unpack(packet[:HEADER.size])
    opcode = header[0]
    payload = packet[HEADER.size:]
    struct_class, result_class = opcode_map.get(opcode)
    return result_class(*(header+struct_class.unpack(payload)))
