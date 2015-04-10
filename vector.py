
import math


class Vector2D:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        if not isinstance(other, Vector2D):
            raise TypeError("Argument to Vector2D.distance should be Vector2D")
        return math.sqrt(
            (other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def square_distance(self, other):
        if not isinstance(other, Vector2D):
            raise TypeError(
                "Argument to Vector2D.square_distance should be Vector2D")
        return (other.x - self.x) ** 2 + (other.y - self.y) ** 2
