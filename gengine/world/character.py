from gengine.vector import Vector2D
from gengine.world.actor import Actor
from gengine.world.shape import Circle

CAPSULE_SIZE = 10
DEFAULT_JUMP_DURATION = 3  # Jump takes 3 seconds
COLLIDABLE_DISTANCE = 3 * CAPSULE_SIZE


class Character(Actor):

    def __init__(self, character_id,
                 initial_position, initial_viewport,
                 timestamp):
        self._world = None  # Will be set upon load into World
        self.timestamp = None  # Will be set upon load into World

        self.character_id = character_id

        self.position = initial_position
        self.viewport = initial_viewport
        self.velocity = Vector2D(0, 0)
        # self._jump_duration = 0
        # self._movement_gen = self._movement_generator()
        # self._pending_events = []

    def geometry(self):
        return Circle(self.position, CAPSULE_SIZE)

    # def _movement_generator(self):
    #     world = self.world
    #     while True:
    #         dt, timestamp = yield
    #         nearby, distance = world.query_nearby(self)
    #         if distance < COLLIDABLE_DISTANCE:
    #             pass
    #             # Perform colliding code here
    #         else:
    #             pass
    #             # Just update position

    # def _reschedule(self):
    #     self._movement_generator

    # def get_bounding_box(self):
    #     return self.capsule.get_bounding_box()

    # def process_till(self, timestamp):
    #     assert self._timestamp < timestamp
    #     dt = timestamp - self._timestamp
    #     self._jump_duration -= dt

    def process_till(self, timestamp):
        dt = timestamp - self.timestamp
        assert dt >= 0, "We can't tick back in time"
        if dt and self.velocity:
            self.position += self.velocity * dt

    def update(
            self,
            timestamp,
            velocity=None,
            viewport=None,
            rotation=None,
            jump=False):
        """ Update movement of character
        """
        # We can't update character data before we process it's possition
        self.process_till(timestamp)

        updated = False
        if viewport and self.viewport != viewport:
            self.viewport = viewport
            updated = True
        if velocity and self.velocity != velocity:
            self.velocity = velocity
            updated = True
        if rotation and self.rotation != rotation:
            self.rotation = rotation
            updated = True

        if jump:
            raise NotImplementedError()

        if updated:
            self._world.update_character(self, timestamp)
