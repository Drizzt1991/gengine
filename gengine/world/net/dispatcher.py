from gengine.protocol.packet import OPCODES, pack_error
from gengine.vector import Vector2D


class ValidationError(Exception):
    """ When packet has invalid data.
    """

    def __init__(self, reason="", fields={}):
        self.reason = reason
        self.fields = fields

    def pack(self):
        pack_error(self.reason, self.fields)


class Dispatcher:

    def __init__(self, net, *, loop):
        self._loop = loop
        self._handlers = {
            OPCODES.CONNECT: self.handle_connect,
            OPCODES.CHAR_MOVE: self.handle_character_movement
        }

    def feed(self, packet):
        handler = self._handlers.get(packet.opcode)
        handler(packet)

    def handle_character_movement(self, packet):
        character = self.world.get_character(packet.character_id)
        velocity = Vector2D(packet.velocity_x, packet.velocity_y)
        viewport = Vector2D(packet.velocity_x, packet.velocity_y)
        if packet.rotation not in [-1, 0, 1]:
            raise ValidationError(
                fields={
                    'rotation': "Not in [-1, 0, 1]"
                })
        character.movement_update(
            velocity=velocity, viewport=viewport, rotation=packet.rotation,
            jump=packet.jump)

    def handle_connect(self, packet):
        if packet.session_id in self.net._connections:
            raise ValidationError(fields={
                "session_id": "Already used"
            })
        connection = self.net._connections[packet.session_id] = \
            self.net.create_connection(packet.session_id)
        connection.start()
