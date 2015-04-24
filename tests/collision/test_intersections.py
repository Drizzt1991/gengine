from unittest import TestCase, skip

from planar import Vec2
from gengine.collision import Circle, BoundingBox, intersects, contains


class TestBBoxToCircle(TestCase):

    def test_no_intersection(self):
        c = Circle(Vec2(0, 0), 2)
        r = BoundingBox.from_center(Vec2(10, 10), 2, 2)
        self.assertFalse(intersects(c, r))
        self.assertFalse(contains(c, r))
        self.assertFalse(contains(r, c))

    def test_circle_in_bbox(self):
        c = Circle(Vec2(0, 0), 2)
        r = BoundingBox.from_center(Vec2(0, 0), 10, 10)
        self.assertTrue(intersects(c, r))
        self.assertTrue(contains(r, c))
        self.assertFalse(contains(c, r))

    def test_bbox_in_circle(self):
        c = Circle(Vec2(0, 0), 10)
        r = BoundingBox.from_center(Vec2(0, 0), 2, 2)
        self.assertTrue(intersects(c, r))
        self.assertTrue(contains(c, r))
        self.assertFalse(contains(r, c))

    def test_intersection(self):
        c = Circle(Vec2(0, 0), 5)
        r = BoundingBox.from_center(Vec2(0, 6), 4, 4)
        self.assertTrue(intersects(c, r))
        self.assertFalse(contains(c, r))
        self.assertFalse(contains(r, c))

    def test_border_intersection(self):
        c = Circle(Vec2(0, 0), 2)
        r = BoundingBox.from_center(Vec2(0, 4), 4, 4)
        self.assertFalse(intersects(c, r))
        self.assertTrue(intersects(c, r, border=True))

    def test_corner_intersection(self):
        # Egyptian triangle (3, 4, 5)
        c = Circle(Vec2(0, 0), 5)
        r = BoundingBox([Vec2(3, 4), Vec2(5, 6)])
        self.assertFalse(intersects(c, r))
        self.assertTrue(intersects(c, r, border=True))

    @skip("contains_point does not work on 0-size polygon")
    def test_circle_in_bbox_border(self):
        # contains have no need for `border` attributes. It always includes
        # border points.
        c = Circle(Vec2(0, 0), 4)
        r = BoundingBox.from_center(Vec2(0, 0), 8, 8)
        self.assertTrue(intersects(c, r))
        self.assertTrue(contains(r, c))
        self.assertFalse(contains(c, r))

    def test_bbox_in_circle_border(self):
        # Egyptian triangle (3, 4, 5)
        c = Circle(Vec2(0, 0), 5)
        r = BoundingBox([Vec2(-3, -4), Vec2(3, 4)])
        self.assertTrue(intersects(c, r))
        self.assertTrue(contains(c, r))
        self.assertFalse(contains(r, c))


class TestBBoxToBBox(TestCase):

    def test_no_intersection(self):
        b1 = BoundingBox([Vec2(0, 0), Vec2(2, 2)])
        b2 = BoundingBox([Vec2(3, 3), Vec2(4, 4)])
        self.assertFalse(intersects(b1, b2))
        self.assertFalse(contains(b1, b2))
        self.assertFalse(contains(b2, b1))

    def test_contains(self):
        b1 = BoundingBox.from_center(Vec2(0, 0), 4, 4)
        b2 = BoundingBox.from_center(Vec2(0, 0), 2, 2)
        self.assertTrue(intersects(b1, b2))
        self.assertTrue(contains(b1, b2))
        self.assertFalse(contains(b2, b1))

    def test_intersects(self):
        b1 = BoundingBox([Vec2(0, 0), Vec2(3, 4)])
        b2 = BoundingBox([Vec2(2, 2), Vec2(5, 7)])
        self.assertTrue(intersects(b1, b2))
        self.assertFalse(contains(b1, b2))
        self.assertFalse(contains(b2, b1))

    def test_border_intersection(self):
        b1 = BoundingBox([Vec2(0, 0), Vec2(2, 4)])
        b2 = BoundingBox([Vec2(2, 2), Vec2(5, 7)])
        self.assertFalse(intersects(b1, b2))
        self.assertTrue(intersects(b1, b2, border=True))
        self.assertFalse(contains(b1, b2))
        self.assertFalse(contains(b2, b1))

    def test_corner_intersection(self):
        b1 = BoundingBox([Vec2(0, 0), Vec2(2, 2)])
        b2 = BoundingBox([Vec2(2, 2), Vec2(5, 7)])
        self.assertFalse(intersects(b1, b2))
        self.assertTrue(intersects(b1, b2, border=True))
        self.assertFalse(contains(b1, b2))
        self.assertFalse(contains(b2, b1))


class TestCircleToCircle(TestCase):

    def test_no_intersection(self):
        c1 = Circle(Vec2(0, 0), 2)
        c2 = Circle(Vec2(10, 10), 2)
        self.assertFalse(intersects(c1, c2))
        self.assertFalse(contains(c1, c2))
        self.assertFalse(contains(c2, c1))

    def test_contains(self):
        c1 = Circle(Vec2(0, 0), 4)
        c2 = Circle(Vec2(0, 0), 2)
        self.assertTrue(intersects(c1, c2))
        self.assertTrue(contains(c1, c2))
        self.assertFalse(contains(c2, c1))

    def test_intersects(self):
        c1 = Circle(Vec2(0, 0), 4)
        c2 = Circle(Vec2(2, 2), 4)
        self.assertTrue(intersects(c1, c2))
        self.assertFalse(contains(c1, c2))
        self.assertFalse(contains(c2, c1))

    def test_border_intersection(self):
        c1 = Circle(Vec2(0, 0), 2)
        c2 = Circle(Vec2(3, 4), 3)
        self.assertFalse(intersects(c1, c2))
        self.assertTrue(intersects(c1, c2, border=True))
        self.assertFalse(contains(c1, c2))
        self.assertFalse(contains(c2, c1))
