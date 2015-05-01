from planar import Vec2

from .shapes import Circle, BoundingBox, Polygon


def bbox_contains_circle(bbox, circle):
    c_radius_2 = 2 * circle.radius
    if bbox.height < c_radius_2 or bbox.width < c_radius_2:
        return False
    # Little simpler to checking bboxes
    inflated = bbox.inflate(-circle.radius * 2)
    if inflated.contains_point(circle.center):
        return True
    return False


def circle_contains_bbox(circle, bbox):
    c_center = circle.center
    c_radius = circle.radius
    min_x, min_y = bbox.min_point
    max_x, max_y = bbox.max_point
    return (
        # Bottom Right
        Vec2(max_x, min_y).distance_to(c_center) <= c_radius and
        # Bottom Left
        Vec2(min_x, min_y).distance_to(c_center) <= c_radius and
        # Upper Right
        Vec2(max_x, max_y).distance_to(c_center) <= c_radius and
        # Upper Left
        Vec2(min_x, max_y).distance_to(c_center) <= c_radius
        )


def circle_contains_circle(circle, other):
    c_radius = circle.radius
    other_radius = other.radius
    radius_diff = c_radius - other_radius
    if radius_diff < 0:
        return False
    # Basicly if other_center is contained in a circle of radius_diff
    return circle.center.distance_to(other.center) <= radius_diff


def bbox_contains_bbox(bbox, other):
    min_x, min_y = bbox.min_point
    max_x, max_y = bbox.max_point
    other_min_x, other_min_y = other.min_point
    other_max_x, other_max_y = other.max_point
    return (
        min_x <= other_min_x and
        max_x >= other_max_x and
        min_y <= other_min_y and
        max_y >= other_max_y
    )


def polygon_contains_bbox(polygon, bbox):
    pol2 = bbox.to_polygon()
    return polygon_contains_polygon(polygon, pol2)


def bbox_contains_polygon(bbox, polygon):
    pol2 = bbox.to_polygon()
    return polygon_contains_polygon(pol2, polygon)


def polygon_contains_polygon(polygon, other):
    for point in other:
        if not polygon.contains_point(point):
            return False
    return True


_registry = {
    (Circle, BoundingBox): circle_contains_bbox,
    (BoundingBox, Circle): bbox_contains_circle,
    (Circle, Circle): circle_contains_circle,
    (BoundingBox, BoundingBox): bbox_contains_bbox,
    (Polygon, BoundingBox): polygon_contains_bbox,
    (BoundingBox, Polygon): bbox_contains_polygon,
    (Polygon, Polygon): polygon_contains_polygon,
}


def contains(container, contained):
    handler = _registry.get((type(container), type(contained)))
    if handler is not None:
        return handler(container, contained)
    raise NotImplementedError
