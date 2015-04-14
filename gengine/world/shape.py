
MASK_ALL = 0xffff


class SimpleObjectIndex:
    """ Will contain object and have interface for querying objects
    """

    def __init__(self):
        self._objects = []

    def add_object(self, geometry, obj, mask=MASK_ALL):
        self._objects.append((geometry, obj, mask))

    def get_objects_circle(self, centre, radius, query_mask=MASK_ALL):
        other = Circle(centre, radius)
        for geometry, obj, obj_mask in self._objects:
            if (query_mask & obj_mask) and geometry.intersection(other):
                yield obj

    def get_nearest_objects(self, centre, max_radius, query_mask=MASK_ALL):
        objs = []
        for geometry, obj, obj_mask in self._objects:
            if (query_mask & obj_mask):
                objs.append((
                    geometry.centre.distance_to(centre),
                    obj
                ))
        objs.sort()
        return [x[0] for x in objs]


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
