import abc
from gengine.utils import lazy_property
from planar import BoundingBox as OriginalBBox, Vec2


class Shape:
    """ Base class for 2D shapes
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def bounding_box(self):
        """ Returns the minimum bbox, that contains the shape
        """
        pass

    @abc.abstractmethod
    def contains_point(self, point):
        """ Return True if point is inside of shape.
            Border inclusion is not defined in abc, is determined by shape's
            use cases.
        """
        pass


class BoundingBox(OriginalBBox, Shape):
    pass


class Circle(Shape):

    def __init__(self, center, radius):
        if not isinstance(center, Vec2):
            center = Vec2(*center)
        self.center = center
        self.radius = radius

    @lazy_property
    def bounding_box(self):
        return BoundingBox.from_center(
            self.center, self.radius*2, self.radius*2)

    def contains_point(self, point):
        d = self.center.distance_to(point)
        return d <= self.radius

    def __repr__(self):
        """Precise string representation."""
        return "Circle((%s, %s), %s)" % (
            self.center.x, self.center.y, self.radius)

    __str__ = __repr__
