from .actor import Actor
from gengine.vector import Vector2D

CAPSULE_SIZE = 10
DEFAULT_JUMP_DURATION = 3  # Jump takes 3 seconds
COLLIDABLE_DISTANCE = 3 * CAPSULE_SIZE


class Character(Actor):

    def __init__(self, world, initial_position, initial_viewport):
        self._world = world

        self._position = initial_position
        self._viewport = initial_viewport
        self._velocity = Vector2D(0, 0)
        self._jump_duration = 0

        self._timestamp = world.time()
        self._movement_gen = self._movement_generator()
        self._pending_events = []

    def _movement_generator(self):
        world = self.world
        while True:
            dt, timestamp = yield
            nearby, distance = world.query_nearby(self)
            if distance < COLLIDABLE_DISTANCE:
                # Perform colliding code here
            else:
                # Just update position



    def _reschedule(self):
        self._movement_generator.

    def get_bounding_box(self):
        return self.capsule.get_bounding_box()

    def process_till(self, timestamp):
        assert self._timestamp < timestamp
        dt = timestamp - self._timestamp
        self._jump_duration -= dt

    def movement_update(
            self,
            timestamp,
            velocity=None,
            viewport=None,
            rotation=None,
            jump=False):
        """ Update movement of character
        """
        updated = False
        if viewport and self._viewport != viewport:
            self._viewport = viewport
            updated = True
        if velocity and self._velocity != velocity:
            self._velocity = velocity
            updated = True
        if rotation and self._rotation != rotation:
            self._rotation = rotation
            updated = True

        if updated:
            self.process_till(timestamp)

        # Do jump if we can
        if self.self._jump_duration == 0 and jump:
            self._jump_duration = DEFAULT_JUMP_DURATION
            self._reschedule()
