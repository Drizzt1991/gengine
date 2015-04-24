from planar import Vec2
from .shapes import BoundingBox
from .intersection import intersects
from .containment import contains


class _QuadNode:

    def __init__(self, parent, bbox, level, *,
                 max_level=None, max_objects=None):
        self._parent = parent
        self._bbox = bbox
        self._level = level
        self._objects = []
        # Nodes
        self._nw = None
        self._sw = None
        self._ne = None
        self._se = None

        if max_level is None:
            max_level = parent._max_level
        self._max_level = max_level
        if max_objects is None:
            max_objects = parent._max_objects
        self._max_objects = max_objects

    @property
    def nodes(self):
        if self._nw is not None:
            return (self._nw, self._ne, self._se, self._sw)
        return ()

    def split(self):
        level = self._level
        if self._nw is not None:
            raise RuntimeError("Already splitted")
        if level == self._max_level:
            raise RuntimeError("Already splitted to max level")

        min_point = self._bbox.min_point
        max_point = self._bbox.max_point
        center_point = self._bbox.center
        min_x, min_y = min_point
        max_x, max_y = max_point
        c_x, c_y = center_point

        new_level = level + 1
        self._nw = self.__class__(
            parent=self,
            bbox=BoundingBox([Vec2(min_x, c_y), Vec2(c_x, max_y)]),
            level=new_level)
        self._sw = self.__class__(
            parent=self,
            bbox=BoundingBox([min_point, center_point]),
            level=new_level)
        self._ne = self.__class__(
            parent=self,
            bbox=BoundingBox([center_point, max_point]),
            level=new_level)
        self._se = self.__class__(
            parent=self,
            bbox=BoundingBox([Vec2(c_x, min_y), Vec2(max_x, c_y)]),
            level=new_level)

    def get_all_objects(self):
        yield from self._objects
        for node in self.nodes:
            yield from node.get_all_objects()

    def clear(self):
        # Clear all children
        for node in self.nodes:
            node.clear()
        # Clear itself then
        self._objects.clear()
        # Clear nodes if we had any
        self._nw = None
        self._sw = None
        self._ne = None
        self._se = None

    def insert(self, bbox, obj):
        # FIXME: We probably can lower the intersection and contains checks.

        # If bbox covers all of this node - add it to objects list and exit.
        if contains(bbox, self._bbox):
            self._objects.append((bbox, obj))
            return
        if not intersects(bbox, self._bbox):
            return
        # If we reached the maximum level of detalisation we will just add it
        # to list of objects
        if self._level == self._max_level:
            self._objects.append((bbox, obj))
            return

        # Check all children for intersections
        if not self.nodes:
            self.split()
        for node in self.nodes:
            node.insert(bbox, obj)

    def remove(self, remove_obj):
        to_remove = None
        for pair in self._objects:
            _, (_, obj) = pair
            if obj is remove_obj:
                to_remove = pair
                # Not like we can insert more than 1 obj.
                break
        if to_remove is not None:
            self._objects.remove(to_remove)
        empty = True
        for node in self.nodes:
            # Remove call will return True if this was the last object
            empty = empty and node.remove(remove_obj)
        if empty:
            self._nw = None
            self._sw = None
            self._ne = None
            self._se = None
            return not self._objects
        return False

    def query(self, bbox):
        # FIXME: When querying we can take height and width to produce a binary
        #        mask of all lowest level quadrants to query for objects
        #        This can add the ability to work with binary masks and
        #        operations to determine intersections, which is very efficient
        if contains(bbox, self._bbox):
            # return all objects
            yield from self.get_all_objects()
            return
        if intersects(bbox, self._bbox):
            yield from self._objects
        for node in self.nodes:
            yield from node.query(bbox)

    def __repr__(self):
        padd = lambda x, t, s='\n': s.join([t+line for line in x.split(s)])
        nodes_repr = "\n".join((repr(node) for node in self.nodes))
        if nodes_repr:
            nodes_repr = '\n' + nodes_repr
        return "_QuadNode<bbox={!r}, objects={!r}, level={}>".format(
            self._bbox, self._objects, self._level) + padd(nodes_repr, '  ')


class QuadTree:

    _quad_node_cls = _QuadNode

    def __init__(self, *, center, size, max_level):
        self._root = self._quad_node_cls(
            parent=None,
            bbox=BoundingBox.from_center(center, size, size),
            level=0,
            max_level=max_level,
            max_objects=1)
        self._size = size
        self._max_level = max_level

    def insert(self, shape, obj):
        bbox = shape.bounding_box
        self._root.insert(bbox, (shape, obj))

    def query_iter(self, query_shape):
        bbox = query_shape.bounding_box
        assert isinstance(bbox, BoundingBox)
        _seen = set([])
        for shape_bbox, (shape, obj) in self._root.query(bbox):
            if obj in _seen:
                continue
            _seen.add(obj)
            if intersects(query_shape, shape):
                yield obj

    def query(self, query_shape):
        return list(self.query_iter(query_shape))

    def remove(self, obj):
        self._root.remove(obj)

    def update(self, shape, obj):
        self.remove(obj)
        self.insert(shape, obj)
