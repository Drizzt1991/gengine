
from unittest import TestCase
from gengine.collision import QuadTree, Circle, BoundingBox
from planar import Vec2


class TestQuadTree(TestCase):
    maxDiff = None

    def setUp(self):
        super().setUp()
        self.tree = QuadTree(
            center=Vec2(0, 0),
            size=80,  # BBOX (-40, -40) to (40, 40)
            max_level=3,  # Min BOX 10X10
            )

    def _get_nodes_data(self, tree):
        return self._get_node_data(tree._root)

    def _get_node_data(self, node):
        data = {
            "level": node._level,
            # "bbox": [
            #     tuple(node._bbox.min_point),
            #     tuple(node._bbox.max_point),
            # ],
        }
        if node._objects:
            data["objects"] = [
                obj for _, (_, obj) in node._objects]

        if node.nodes:
            data['nodes'] = nodes = []
            for inner_node in node.nodes:
                nodes.append(self._get_node_data(inner_node))
        return data

    def test_query(self):
        x = Circle(Vec2(30, 30), 10)
        y = Circle(Vec2(-10, -10), 10)
        z = Circle(Vec2(0, 0), 10)
        self.tree.insert(x, x)
        self.tree.insert(y, y)
        self.tree.insert(z, z)

        # Helper to ignore results order
        o = lambda x: list(sorted(x, key=lambda x: x.center.x))

        # Contains circle
        results = self.tree.query(
            BoundingBox.from_center(Vec2(30, 30), 22, 22))
        self.assertEqual(results, [x])
        # Intersect circle
        results = self.tree.query(
            BoundingBox.from_center(Vec2(20, 40), 10, 10))
        self.assertEqual(results, [x])
        # Is contained in circle
        results = self.tree.query(
            BoundingBox.from_center(Vec2(30, 30), 10, 10))
        self.assertEqual(results, [x])

        # Contains 2 circles
        results = self.tree.query(
            BoundingBox.from_center(Vec2(-5, -5), 32, 32))
        self.assertEqual(o(results), o([y, z]))
        # Intersect 2 circles
        results = self.tree.query(
            BoundingBox.from_center(Vec2(-10, 0), 2, 2))
        self.assertEqual(o(results), o([y, z]))
        # Contained in 2 circles
        results = self.tree.query(
            BoundingBox.from_center(Vec2(-5, -5), 2, 2))
        self.assertEqual(o(results), o([y, z]))

        # Contained in 1 of circles
        results = self.tree.query(
            BoundingBox.from_center(Vec2(-10, -10), 2, 2))
        self.assertEqual(results, [y])

        # Contain all circles
        results = self.tree.query(
            BoundingBox.from_center(Vec2(0, 0), 80, 80))
        self.assertEqual(o(results), o([x, y, z]))

    def test_insert_single_quadrant(self):
        # In [(0, 0), (10, 10)] quadrant
        bbox = BoundingBox([Vec2(1, 1), Vec2(4, 4)])
        self.tree.insert(bbox, bbox)

        self.assertEqual(self._get_nodes_data(self.tree), {
            "level": 0, "nodes": [
                {"level": 1},
                {"level": 1, "nodes": [
                    {"level": 2},
                    {"level": 2},
                    {"level": 2},
                    {"level": 2, "nodes": [
                        {"level": 3},
                        {"level": 3},
                        {"level": 3},
                        {"level": 3, "objects": [bbox]}
                    ]},
                ]},
                {"level": 1},
                {"level": 1},
            ]
        })

    def test_insert_two_quadrants(self):
        bbox = BoundingBox([Vec2(1, -1), Vec2(4, 4)])
        self.tree.insert(bbox, bbox)

        self.assertEqual(self._get_nodes_data(self.tree), {
            "level": 0, "nodes": [
                {"level": 1},
                {"level": 1, "nodes": [
                    {"level": 2},
                    {"level": 2},
                    {"level": 2},
                    {"level": 2, "nodes": [
                        {"level": 3},
                        {"level": 3},
                        {"level": 3},
                        {"level": 3, "objects": [bbox]}
                    ]},
                ]},
                {"level": 1, "nodes": [
                    {"level": 2, "nodes": [
                        {"level": 3, "objects": [bbox]},
                        {"level": 3},
                        {"level": 3},
                        {"level": 3},
                    ]},
                    {"level": 2},
                    {"level": 2},
                    {"level": 2},
                ]},
                {"level": 1},
            ]
        })

    def test_insert_four_quadrants(self):
        bbox = BoundingBox([Vec2(-2, -2), Vec2(2, 5)])
        self.tree.insert(bbox, bbox)

        self.assertEqual(self._get_nodes_data(self.tree), {
            "level": 0, "nodes": [
                {"level": 1, "nodes": [
                    {"level": 2},
                    {"level": 2},
                    {"level": 2, "nodes": [
                        {"level": 3},
                        {"level": 3},
                        {"level": 3, "objects": [bbox]},
                        {"level": 3},
                    ]},
                    {"level": 2},
                ]},
                {"level": 1, "nodes": [
                    {"level": 2},
                    {"level": 2},
                    {"level": 2},
                    {"level": 2, "nodes": [
                        {"level": 3},
                        {"level": 3},
                        {"level": 3},
                        {"level": 3, "objects": [bbox]}
                    ]},
                ]},
                {"level": 1, "nodes": [
                    {"level": 2, "nodes": [
                        {"level": 3, "objects": [bbox]},
                        {"level": 3},
                        {"level": 3},
                        {"level": 3},
                    ]},
                    {"level": 2},
                    {"level": 2},
                    {"level": 2},
                ]},
                {"level": 1, "nodes": [
                    {"level": 2},
                    {"level": 2, "nodes": [
                        {"level": 3},
                        {"level": 3, "objects": [bbox]},
                        {"level": 3},
                        {"level": 3},
                    ]},
                    {"level": 2},
                    {"level": 2},
                ]},
            ]
        })
