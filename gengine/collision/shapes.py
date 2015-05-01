import abc
from gengine.utils import lazy_property
from planar import BoundingBox as OriginalBBox, Vec2
from planar.line import LineSegment as OriginalLineSegment
from planar.polygon import Polygon as OriginalPolygon  # Segfault on C impl =(.


__all__ = [
    "Shape",
    "LineSegment",
    "BoundingBox",
    "Circle"
]


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

    def to_polygon(self):
        min_bbox, max_bbox = self.min_point, self.max_point
        return Polygon([
            min_bbox, (min_bbox.x, max_bbox.y),
            max_bbox, (max_bbox.x, min_bbox.y)],
            is_convex=True)


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


class LineSegment(OriginalLineSegment, Shape):

    @lazy_property
    def bounding_box(self):
        return BoundingBox(self.points)


class Polygon(OriginalPolygon, Shape):

    def iter_edges(self):
        for i in range(len(self)):
            yield LineSegment.from_points([self[i], self[i - 1]])

    def project(self, vector):
        min_point = max_point = vector.dot(self[0])
        for vertice in self:
            x = vector.dot(vertice)
            if x < min_point:
                min_point = x
            if x > max_point:
                max_point = x
        return min_point, max_point
