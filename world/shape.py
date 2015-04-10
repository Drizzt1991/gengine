from copy import copy

MASK_ALL = 0xffff


class SimpleObjectIndex:
    """ Will contain object and have interface for querying objects
    """

    def __init__(self):
        self._objects = []

    def add_object(self, geometry, obj, mask=MASK_ALL):
        self.objects.append((geometry, obj, mask))

    def get_objects_circle(self, centre, radius, query_mask=MASK_ALL):
        other = Circle(centre, radius)
        for geometry, obj, obj_mask in self._objects:
            if (query_mask & obj_mask) and geometry.intersection(other):
                yield obj

    def get_nearest_objects(self, centre, max_radius, query_mask=MASK_ALL):
        if max_radius:
            objs = list(self.get_objects_circle(
                centre, max_radius, query_mask=query_mask))
        else:
            # Copy for resorting
            objs = copy(self._objects)
        objs.sort(key=lambda x: centre.distance(x.centre))
        return objs


class Geometry:
    """ Base class for 2D shapes
    """


class Circle(Geometry):

    def __init__(self, centre, radius):
        self.centre = centre
        self.radius = radius

    def intersection(self, other):
        if isinstance(other, (Circle)):
            return (self.centre.distance(other.centre) <
                    self.radius + other.radius)
        else:
            raise NotImplementedError()
