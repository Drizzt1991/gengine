import math
from collections import namedtuple


class Vector2D(namedtuple('Vector2D', ('x', 'y'))):
    __slots__ = ()

    def __abs__(self):
        return type(self)(abs(self.x), abs(self.y))

    def __add__(self, other):
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return type(self)(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return type(self)(self.x * other, self.y * other)

    def __div__(self, other):
        return type(self)(self.x / other, self.y / other)

    def __bool__(self):
        return not (self.x == 0 and self.y == 0)

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        """ uses the Euclidean norm to calculate the distance """
        return math.hypot((self.x - other.x), (self.y - other.y))

    @classmethod
    def from_deg(self, deg):
        """ Returns 1 length vector pointing at ``deg`` angle to X axis.
        """
        rad = math.radians(deg)
        return Vector2D(math.cos(rad), math.sin(rad))

    def __repr__(self):
        return 'Vector2D({}, {})'.format(self.x, self.y)
