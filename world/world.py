from .world_map import load_map
from gengine.vector import Vector2D


NEARBY_RADIUS = 20


class World:

    def __init__(self, map_file, *, loop):
        self._loop = loop
        self._map = load_map(map_file)

    def time(self):
        return self._loop.time()

    def get_character(self, character_id):
        return self._characters.get(character_id)

    def query_characters_circle(self, timestamp, centre, radius):
        """ Find all characters, that are in circle.
        """
        suspects = self._aabbtree.get_objects_circle(centre, radius)
        results = []
        for character in suspects:
            character.process_till(timestamp)
            intersection = character.in_circle(centre, radius)
            if intersection:
                results.append((character, intersection))
        return results

    def query_nearby(self, character):
        """ Finds objects, that are near character. Iterator.
        """
        return self._aabbtree.iter_objects(
            character.position, NEARBY_RADIUS)
