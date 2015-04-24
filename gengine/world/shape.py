CAPSULE_SIZE = 10
MASK_ALL = 0xffff


class SimpleObjectIndex:
    """ Will contain object and have interface for querying objects
    """

    def __init__(self):
        self._objects = {}

    def update_character(self, obj):
        geometry = Circle(centre=obj.position, radius=CAPSULE_SIZE)
        self._objects[obj.character_id] = (geometry, obj, MASK_ALL)

    def get_objects_circle(self, centre, radius, query_mask=MASK_ALL):
        other = Circle(centre, radius)
        for geometry, obj, obj_mask in self._objects.values():
            if (query_mask & obj_mask) and geometry.intersection(other):
                yield obj

    def get_nearest_objects(self, centre, max_radius, query_mask=MASK_ALL):
        objs = []
        for geometry, obj, obj_mask in self._objects.values():
            if (query_mask & obj_mask):
                objs.append((
                    geometry.centre.distance_to(centre),
                    obj
                ))
        objs.sort()
        return [x[1] for x in objs]

    def get_collisions(
            self, position, timestamp, predicted_position, reschedule_time):
        return []


class Geometry:
    """ Base class for 2D shapes
    """


class Circle(Geometry):

    def __init__(self, centre, radius):
        self.centre = centre
        self.radius = radius

    def intersection(self, other):
        if isinstance(other, (Circle)):
            return (self.centre.distance_to(other.centre) <
                    self.radius + other.radius)
        else:
            raise NotImplementedError()

    def get_bbox(self):
        return
