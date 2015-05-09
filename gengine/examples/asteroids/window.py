import math
import pyglet
from pyglet.window import key


from pyglet.gl import (
    glBegin,
    glVertex2f,
    glEnd,
    glDisable,
    glViewport,
    glMatrixMode,
    glLoadIdentity,
    glOrtho,
    GL_TRIANGLE_FAN,
    GL_DEPTH_TEST,
    GL_PROJECTION,
    GL_MODELVIEW,
    GL_LINES,
    glScalef
    )

COLLISION_RADIUS = 3


class GameWindow(pyglet.window.Window):

    SPACE_TTL = 0.08
    LEFT_TTL = 1 / 30
    RIGHT_TTL = 1 / 30
    UP_TTL = 1 / 10

    def __init__(self, world, *args, **kw):
        super().__init__(*args, **kw)
        self._world = world
        self.fps_display = pyglet.clock.ClockDisplay()
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule_interval(self._tick, 1 / 60)
        # Key trottle times
        self._last_calls = {}

    def _tick(self, dt):
        self._world.advance_by(dt)
        self.check_keys()

    def check_keys(self):
        timestamp = self._world.time()
        if self.keys[key.SPACE]:
            last_called = self._last_calls.get(key.SPACE, 0)
            if timestamp - last_called >= self.SPACE_TTL:
                self._last_calls[key.SPACE] = timestamp
                self.trigger_space(timestamp)
        if self.keys[key.LEFT]:
            last_called = self._last_calls.get(key.LEFT, 0)
            if timestamp - last_called >= self.LEFT_TTL:
                self._last_calls[key.LEFT] = timestamp
                self.trigger_left(timestamp)
        if self.keys[key.RIGHT]:
            last_called = self._last_calls.get(key.RIGHT, 0)
            if timestamp - last_called >= self.RIGHT_TTL:
                self._last_calls[key.RIGHT] = timestamp
                self.trigger_right(timestamp)
        if self.keys[key.UP]:
            last_called = self._last_calls.get(key.UP, 0)
            if timestamp - last_called >= self.UP_TTL:
                self._last_calls[key.UP] = timestamp
                self.trigger_up(timestamp)

    def trigger_space(self, timestamp):
        self._world.player.fire_bullet(timestamp)

    def trigger_left(self, timestamp):
        self._world.player.rotate(timestamp, 1)

    def trigger_right(self, timestamp):
        self._world.player.rotate(timestamp, -1)

    def trigger_up(self, timestamp):
        self._world.player.bump(timestamp)

    def on_draw(self):
        self.clear()
        self.set_2d()
        self._draw_static()
        self._draw_objects()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.fps_display.draw()

    def _draw_static(self):
        # No static for now =)
        pass

    def _draw_objects(self):
        timestamp = self._world.time()
        for component in self._world._objects:
            component.draw(timestamp)

    def set_2d(self):
        screen_width, screen_height = self.get_size()
        width, height = self._world.width, self._world.height

        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, screen_width, screen_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(
            -screen_width/2, screen_width/2,
            -screen_height/2, screen_height/2,
            -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # We add 10% to bounds so Asteroids port between bounds smoothly
        glScalef(screen_width / width * 1.1,
                 screen_height / height * 1.1, 1.0)


def circle(x, y, radius):
    """
    We want a pixel perfect circle. To get one,
    we have to approximate it densely with triangles.
    Each triangle thinner than a pixel is enough
    to do it. Sin and cosine are calculated once
    and then used repeatedly to rotate the vector.
    I dropped 10 iterations intentionally for fun.
    """
    iterations = int(2*radius*math.pi)
    s = math.sin(2*math.pi / iterations)
    c = math.cos(2*math.pi / iterations)

    dx, dy = radius, 0

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(iterations+1):
        glVertex2f(x+dx, y+dy)
        dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    glEnd()
