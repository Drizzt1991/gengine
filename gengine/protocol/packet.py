import struct
import msgpack
from collections import namedtuple

OPCODE_STRUCT = struct.Struct("H")
HEADER_STRUCT = struct.Struct("HdI")

header_fields = ['opcode', 'timestamp', 'sequence_id', 'session_id']

# Connect
# Client -> Server
CONNECT_STRUCT = struct.Struct(
    "8s")
Connect = namedtuple(
    "Connect",
    header_fields)

# Character init
# Server -> Client
CHAR_UPDATE_STRUCT = struct.Struct(
    "QffffffBb")
CharacterUpdate = namedtuple(
    "CharacterInit",
    header_fields + [
        "character_id",
        "position_x", "position_y",
        "velocity_x", "velocity_y",
        "viewport_x", "viewport_y",
        "jump", "rotation"
    ])


# Character movement
# Client -> Server
CHAR_MOVE_STRUCT = struct.Struct(
    "QffffBb")
CharacterMovement = namedtuple(
    "CharacterMovement",
    header_fields + [
        "character_id",
        "velocity_x", "velocity_y",
        "viewport_x", "viewport_y",
        "jump", "rotation"
    ])

# ACK
# Server -> Client
# Client -> Server
ACK_STRUCT = struct.Struct("HdIH")
ACK = namedtuple(
    "ACK",
    [
        "opcode",
        "timestamp",
        "ack_sequence_id",  # ACK do not have their sequence_id,
                            # but send acked ID instead
        "ack_opcode"
    ])


class OPCODES:

    CONNECT = 0x10
    CHAR_UPDATE = 0x30
    CHAR_MOVE = 0x31
    ERROR = 0x90
    ACK = 0x91

_opcode_map = {
    OPCODES.CONNECT: (CONNECT_STRUCT, Connect),
    OPCODES.CHAR_MOVE: (CHAR_MOVE_STRUCT, CharacterMovement),
    OPCODES.CHAR_UPDATE: (CHAR_UPDATE_STRUCT, CharacterUpdate)
}


ChannelMeta = namedtuple("PacketMeta", ["channel_id", "ack"])

_opcode_meta = {
    OPCODES.CONNECT: ChannelMeta(channel_id=0x10, ack=True),
    OPCODES.CHAR_MOVE: ChannelMeta(channel_id=0x30, ack=False),
    OPCODES.CHAR_UPDATE: ChannelMeta(channel_id=0x30, ack=False)
}


def parse(raw_packet, _opcode_map=_opcode_map):
    opcode = OPCODE_STRUCT.unpack(raw_packet[:OPCODE_STRUCT.size])[0]
    if opcode == OPCODES.ERROR:
        return msgpack.loads(raw_packet[OPCODE_STRUCT.size:])
    elif opcode == OPCODES.ACK:
        return ACK(*ACK_STRUCT.unpack(raw_packet))
    else:
        header = HEADER_STRUCT.unpack(raw_packet[:HEADER_STRUCT.size])
        payload = raw_packet[HEADER_STRUCT.size:]
        try:
            struct_class, result_class = _opcode_map[opcode]
        except KeyError:
            raise ValueError("Opcode {:x} not implemented".format(opcode))
        return result_class(*(header+struct_class.unpack(payload)))


def pack(opcode, _opcode_map=_opcode_map, **data):
    struct_class, result_class = _opcode_map.get(opcode)
    packet = result_class(
        opcode=opcode,
        **data)
    return (
        HEADER_STRUCT.pack(*packet[:len(header_fields)]) +
        struct_class.pack(*packet[len(header_fields):])
        )


def pack_error(reason, fields):
    payload = msgpack.dumps({"reason": reason, "fields": fields})
    return OPCODES.ERROR + payload


def get_channel(opcode):
    return _opcode_meta[opcode]


def form_ack(packet):
    return ACK_STRUCT.pack(
        OPCODES.ACK,
        packet.timestamp,
        packet.sequence_id,
        packet.opcode)
