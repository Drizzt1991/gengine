import functools
from planar import Vec2

from .shapes import Circle, BoundingBox


def inverse(func):
    @functools.wraps(func)
    def do(left, right, **kw):
        return func(right, left, **kw)
    return do


def circle_to_bbox(circle, bbox, border=False):
    c_center = circle.center
    c_radius = circle.radius
    c_x, c_y = c_center

    # Fast check for optimistic cases
    if bbox.contains_point(c_center):
        return True
    # Little simpler to checking bboxes
    inflated = bbox.inflate(c_radius * 2)
    if not inflated.contains_point(c_center):
        # Lower and left bounds are not border inclusive. Should respect
        # `border` option
        inf_min_x, inf_min_y = inflated.min_point
        inf_max_x, inf_max_y = inflated.max_point
        if not (border and (
                (c_x == inf_min_x and inf_min_y < c_y < inf_max_y) or
                (c_y == inf_min_y and inf_min_x < c_x < inf_max_x))):
            return False

    min_x, min_y = bbox.min_point
    max_x, max_y = bbox.max_point
    # Any chance we don't have collision is when circle is near corners
    # Below
    if c_y < min_y:
        # Below Right
        if c_x > max_x:
            d = Vec2(max_x, min_y).distance_to(c_center)
        # Below Left
        elif c_x < min_x:
            d = Vec2(min_x, min_y).distance_to(c_center)
        else:
            return True
    # Above
    elif c_y > max_y:
        # Above Right
        if c_x > max_x:
            d = Vec2(max_x, max_y).distance_to(c_center)
        # Above Left
        elif c_x < min_x:
            d = Vec2(min_x, max_y).distance_to(c_center)
        else:
            return True
    else:
        return True
    # Check if center is far enough from corner
    if border and d > c_radius:
        return False
    if not border and d >= c_radius:
        return False
    return True


def circle_to_circle(circle, other, border=False):
    d = circle.center.distance_to(other.center)
    r_sum = circle.radius + other.radius
    if d > r_sum:
        return False
    if d < r_sum:
        return True
    return border


def bbox_to_bbox(bbox, other, border=False):
    min_x, min_y = bbox.min_point
    max_x, max_y = bbox.max_point
    other_min_x, other_min_y = other.min_point
    other_max_x, other_max_y = other.max_point
    if border:
        return not (
            # Below
            min_y > other_max_y or
            # Above
            max_y < other_min_y or
            # Left
            min_x > other_max_x or
            # Right
            max_x < other_min_x
            )
    else:
        return not (
            # Below
            min_y >= other_max_y or
            # Above
            max_y <= other_min_y or
            # Left
            min_x >= other_max_x or
            # Right
            max_x <= other_min_x
            )

_registry = {
    (Circle, BoundingBox): circle_to_bbox,
    (BoundingBox, Circle): inverse(circle_to_bbox),
    (Circle, Circle): circle_to_circle,
    (BoundingBox, BoundingBox): bbox_to_bbox
}


def intersects(right, left, border=False):
    handler = _registry.get((type(right), type(left)))
    if handler is not None:
        return handler(right, left, border=border)
    raise NotImplementedError
