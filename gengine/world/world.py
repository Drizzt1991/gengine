
# from gengine.world.character import Character
from gengine.world.shape import SimpleObjectIndex
# from gengine.vector import Vector2D

NEARBY_RADIUS = 20
COMPONENT_SCHEDULE_AHEAD = 1
SCHEDULE_DELTA = 0.01


class World:

    def __init__(self, *, loop):
        self._loop = loop
        self._characters = {}
        self._object_index = SimpleObjectIndex()

    def load_character(self, character, *, timestamp):
        # Add character to listeners
        self._characters[character.character_id] = character
        self._object_index.add_object(character.geometry(), character)
        # Bind character to this world
        character._world = self
        character.timestamp = timestamp

        # Notify subscribers
        affected = self._object_index.get_nearest_objects(
            character.position, NEARBY_RADIUS)
        self.notify(
            event="character_load",
            affects=affected,
            character=character,
            timestamp=timestamp)

    def update_character(self, character, timestamp):
        # Update position based on velocity
        character.process_till(timestamp)
        new_geometry = character.geometry()
        # XXX: Unschedule old collision events
        # Find first pending collision and process it
        collisions = self._object_index.get_collisions(new_geometry)
        assert not collisions  # XXX: Fix up geometry if needed
        # If none just set update to be done in X sec
        new_timestamp = timestamp + COMPONENT_SCHEDULE_AHEAD
        self._loop.call_at(
            new_timestamp-SCHEDULE_DELTA,
            self.update_character, new_timestamp)

    def unload_character(self):
        pass

    def notify(self, event, affects, timestamp, **event_data):
        pass

    # def login_character(self, character_id):
    #     if character_id in self._characters:
    #         raise ValueError("This character is already logged in")
    #     self._characters[character_id] = Character(
    #         character_id=character_id,
    #         world=self,
    #         initial_position=Vector2D(200, 200),
    #         initial_vector=Vector2D(0, 0))
    #     self.net.notify_character_login(
    #         self._characters[character_id], timestamp=self.time())

    # def get_character(self, character_id):
    #     return self._characters.get(character_id)

    # def query_characters_circle(self, timestamp, centre, radius):
    #     """ Find all characters, that are in circle.
    #     """
    #     suspects = self._aabbtree.get_objects_circle(centre, radius)
    #     results = []
    #     for character in suspects:
    #         character.process_till(timestamp)
    #         intersection = character.in_circle(centre, radius)
    #         if intersection:
    #             results.append((character, intersection))
    #     return results

    # def close(self):
    #     pass
