import abc
import math
from planar import Vec2, Affine
from pyglet.gl import GL_LINE_LOOP
from pyglet.graphics import draw as gl_draw

from gengine.collision import Shape, Polygon, Circle


class Component:
    __metaclass__ = abc.ABCMeta

    _world = None

    def __init__(
            self,
            position: Vec2,
            shape: Shape,
            timestamp: int):
        self._position = position
        self._shape = shape
        self._timestamp = timestamp

    @property
    def shape(self):
        return self._shape

    @property
    def position(self):
        return self._position

    @property
    def timestamp(self):
        return self._timestamp


class PolygonComponent(Component):

    def draw(self, timestamp):
        dt = timestamp - self.timestamp
        shape = self.shape
        transform = self._get_transform(dt)
        n_points = len(shape)
        flatten_array = []
        for vertice in shape:
            flatten_array.extend(vertice * transform)
        gl_draw(n_points, GL_LINE_LOOP, ('v2f', flatten_array))

    def _get_transform(self, dt):
        position = Affine.translation(self._position + self._velocity * dt)
        return position


class Asteroid(PolygonComponent):

    ROTATION_SPEED = 60   # deg/s

    def __init__(
            self,
            position: Vec2,
            velocity: Vec2,
            timestamp: int):
        shape = Polygon([
            Vec2(2, 4), Vec2(4, 2),
            Vec2(2, 1), Vec2(5, -1),
            Vec2(2, -4), Vec2(-2, -4),
            Vec2(-4, -2), Vec2(-4, 2),
            Vec2(-2, 4), Vec2(0, 3),
            ])
        self.radius = max((ob.length for ob in shape))
        super().__init__(position, shape, timestamp)
        self._velocity = velocity

    def _get_transform(self, dt):
        # Set rotation in analogue to direction of velocity
        position = Affine.translation(self._position + self._velocity * dt)
        return position

    def _update_time(self, timestamp):
        dt = timestamp - self._timestamp
        self._position = self._position + self._velocity * dt
        self._timestamp = timestamp


class Bullet(PolygonComponent):

    BULLET_SPEED = 120
    BULLET_TTL = 0.8

    def __init__(
            self,
            position: Vec2,
            direction: Vec2,
            timestamp: int):
        r = self.radius = 0.15
        self.ttl = self.BULLET_TTL
        shape = Polygon([
            Vec2(r, r), Vec2(-r, r),
            Vec2(-r, -r), Vec2(r, -r),
            ])
        super().__init__(position, shape, timestamp)
        self._velocity = direction * self.BULLET_SPEED

    def draw(self, timestamp):
        assert self.timestamp + self.ttl > timestamp, \
            "Why do we draw an expired bullet"
        super().draw(timestamp)

    def _get_transform(self, dt):
        # Set rotation in analogue to direction of velocity
        rotation = Affine.rotation(self._velocity.angle)
        position = Affine.translation(self._position + self._velocity * dt)
        return position * rotation

    def _update_time(self, timestamp):
        dt = timestamp - self._timestamp
        self._position = self._position + self._velocity * dt
        self._timestamp = timestamp


class SpaceShip(PolygonComponent):

    ROTATION_SPEED = 12  # deg / s
    BUMP_AMPLITUDE = 10
    DECELERATION = 0.5

    def __init__(
            self,
            position: Vec2,
            velocity: Vec2,
            angle: int,
            timestamp: int,
            ):
        shape = Polygon([
            Vec2(4, 0), Vec2(-2, -2),
            Vec2(-1, 0), Vec2(-2, 2),
            ])
        super().__init__(position, shape, timestamp)
        self._velocity = velocity
        self._angle = angle

    def _get_transform(self, dt):
        # Set rotation in analogue to direction of velocity
        rotation = Affine.rotation(self._angle)
        position = Affine.translation(self._position_in(dt))
        return position * rotation

    def _position_in(self, dt):
        # integral v/(1+b t) dt = (v log(b t+1))/b+constant
        # where v - velocity, b - DECELERATION
        return self._position + (
            self._velocity * (
                math.log(self.DECELERATION * dt + 1) / self.DECELERATION))

    def _velocity_in(self, dt):
        # v/(1+b t)
        # where v - velocity, b - DECELERATION
        return self._velocity / (1 + self.DECELERATION * dt)

    def _update_time(self, timestamp):
        dt = timestamp - self._timestamp
        self._position = self._position_in(dt)
        self._velocity = self._velocity_in(dt)
        self._timestamp = timestamp

    def bump(self, timestamp):
        self._update_time(timestamp)
        direction = Vec2.polar(self._angle)
        self._velocity += direction * self.BUMP_AMPLITUDE
        # FIXME: Reschedule world

    def rotate(self, timestamp, direction):
        if direction not in [1, -1]:
            raise ValueError("`direction` should be 1 or -1")

        self._update_time(timestamp)
        self._angle += direction * self.ROTATION_SPEED
        # FIXME: Reschedule world

    def fire_bullet(self, timestamp):
        dt = timestamp - self._timestamp
        position = self._position_in(dt)
        # Bullet is created at pin of the ship. Which is 4 units further than
        # center
        direction = Vec2.polar(self._angle)
        position += direction * 4

        bullet = Bullet(
            position, direction, timestamp)

        self._world._add_bullet(timestamp, bullet)
