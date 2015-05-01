from .shapes import Shape, LineSegment
from gengine.util import lazy_property


class MovingShape(Shape):
    """ Base class for shapes, that have a movement vector
    """
    pass


class MovingCircle(MovingShape):

    def __init__(self, seg, radius, timestamp, dt):
        self.seg = seg
        self.radius = radius
        self.timestamp = timestamp
        self.dt = dt

    @classmethod
    def from_velocity(cls, initial_circle, velocity, timestamp, dt):
        initial = initial_circle.center
        radius = initial_circle.radius
        seg = LineSegment.from_points(initial, velocity * dt)
        return cls(seg, radius, timestamp, dt)

    @lazy_property
    def bounding_box(self):
        return self.seg.bounding_box.inflate(self.radius*2)

    def contains_point(self, point):
        d = self.seg.distance_to(point)
        return d <= self.radius

    def __repr__(self):
        """Precise string representation."""
        return "MovingCircle(%s, %s, %s, %s, %s)" % (
            self.initial, self.ending, self.radius, self.timestamp, self.dt)

    __str__ = __repr__
