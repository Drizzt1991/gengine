from gengine.world import World
from gengine.component import dep, component
from gengine.net.packet import parse as packet_parse, OPCODES
from gengine.vector import Vector2D


class ValidationError(Exception):
    """ When packet has invalid data.
    """


@component
class Dispatcher:

    world = dep(World)

    def __init__(self, *, loop):
        self._loop = loop
        self._handlers = {
            OPCODES.CHAR_MOVE: self.handle_character_movement
        }

    def feed_raw(self, packet):
        parsed = packet_parse(packet)
        handler = self._handlers.get(parsed.opcode)
        handler(parsed)

    def handle_character_movement(self, packet):
        character = self.world.get_character(packet.character_id)
        velocity = Vector2D(packet.velocity_x, packet.velocity_y)
        viewport = Vector2D(packet.velocity_x, packet.velocity_y)
        if packet.rotation not in [-1, 0, 1]:
            raise ValidationError(fields={
                'rotation': "Not in [-1, 0, 1]"
            })
        character.movement_update(
            velocity=velocity, viewport=viewport, rotation=packet.rotation,
            jump=packet.jump)
