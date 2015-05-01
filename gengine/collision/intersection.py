import functools
import itertools as it
from planar import Vec2

from .shapes import Circle, BoundingBox, Polygon


def inverse(func):
    @functools.wraps(func)
    def do(left, right, **kw):
        return func(right, left, **kw)
    return do


def moving_circle_to_circle(mcircle, other, border=False):
    d = mcircle.seg.distance_to(other.center)
    if border:
        return d <= (other.radius + mcircle.radius)
    else:
        return d < (other.radius + mcircle.radius)


def moving_circle_to_bbox(mcircle, bbox):
    p1, p2 = mcircle.seg.points()
    r = mcircle.radius
    n = mcircle.seg.normal
    # We will check 3 parts - inital and ending positions and shaft between
    c1 = Circle(p1, r)
    c2 = Circle(p2, r)
    pol = Polygon([
        p1 + n * r,
        p1 - n * r,
        p2 - n * r,
        p2 + n * r],
        is_convex=True)
    return (
        intersects(c1, bbox) or
        intersects(c2, bbox) or
        intersects(pol, bbox))


def moving_circle_to_moving_circle(mcircle, other, border=False):
    # Find Closest point of approach (CPA)
    # http://geomalgorithms.com/a07-_distance.html
    dv = mcircle.velocity - other.velocity
    # If velocities are equal just assume parallel lines
    if dv.is_null:
        cpa_time = 0
    else:
        dv2 = dv.dot(dv)
        w0 = mcircle.center - other.center
        cpa_time = - w0.dot(dv) / dv2

    if cpa_time <= 0:
        # We had closes point earlier of directly at start
        pass  # FIXME
    elif cpa_time > mcircle.dt and cpa_time > other.dt:
        pass  # FIXME
    else:
        c1 = mcircle.at(cpa_time)
        c2 = other.at(cpa_time)
        d = c1.center.distance_to(c2.center)
        r_sum = c1.radius + c2.radius
        if d > r_sum:
            return False
        if d < r_sum:
            return True
        return border


def polygon_to_bbox(polygon, bbox, border=False):
    pol2 = bbox.to_polygon()
    return polygon_to_polygon(polygon, pol2, border=border)


def polygon_to_polygon(polygon, other, border=False):
    # FIXME: We can skip projecting the owner of edge, cause we can know
    # exactly where is the maximum point (0, for this normal)

    # SAT or Separating Axis Theorem.
    # If we have a plane, on which projections of shapes do not intersect, than
    # objects don't intersect
    _seen = set([])
    for edge in it.chain(polygon.iter_edges(), other.iter_edges()):
        # Ignore projections on the same normal vectors.
        # Useful for enhancing paralelogram tests
        edge_normal = edge.normal
        if edge_normal in _seen:
            continue
        _seen.add(edge.normal)
        # We project on 1d plane so only 1 coordinate
        min_x, max_x = polygon.project(edge_normal)
        other_min, other_max = other.project(edge_normal)
        if border:
            if min_x > other_max or max_x < other_min:
                return False
        else:
            if min_x >= other_max or max_x <= other_min:
                return False
    return True


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
    (BoundingBox, BoundingBox): bbox_to_bbox,
    (Polygon, BoundingBox): polygon_to_bbox,
    (BoundingBox, Polygon): inverse(polygon_to_bbox),
    (Polygon, Polygon): polygon_to_polygon
}


def intersects(right, left, border=False):
    handler = _registry.get((type(right), type(left)))
    if handler is not None:
        return handler(right, left, border=border)
    raise NotImplementedError
