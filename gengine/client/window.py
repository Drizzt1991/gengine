import math
import pyglet
import random

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
    GL_LINES
    )

from gengine.vector import Vector2D

COLLISION_RADIUS = 3


class GameWindow(pyglet.window.Window):

    def __init__(self, world, event_queue, *args, **kw):
        super().__init__(*args, **kw)
        self._world = world
        self._events = event_queue
        self.fps_display = pyglet.clock.ClockDisplay()
        pyglet.clock.schedule_interval(self._tick, 1 / 60)
        pyglet.clock.schedule_interval(self._tick_position, 1 / 60)
        pyglet.clock.schedule_interval(self._tick_viewport, 1)

    def _tick_position(self, dt):
        character = self._world._characters[0]
        new_position = character.position + character.viewport * 0.4
        character.update(position=new_position)

    def _tick_viewport(self, dt):
        character = self._world._characters[0]
        ang = random.random() * math.pi
        viewport = Vector2D(math.cos(ang), math.sin(ang))
        character.update(viewport=viewport)

    def _tick(self, dt):
        if not self._events.empty:
            packet, addr = self.event_queue.get_nowait()
            print(packet, addr)

    def on_draw(self):
        self.clear()
        self.set_2d()
        self._draw_pawns()
        self.fps_display.draw()

    def _draw_pawns(self):
        width, height = self.get_size()

        for pawn in self._world._characters:
            x, y = pawn.position
            circle(int(x), int(y), COLLISION_RADIUS)
            vx, vy = pawn.viewport
            view_arrow_length = 20
            vx = int(x + vx * view_arrow_length)
            vy = int(y + vy * view_arrow_length)
            pyglet.graphics.draw(
                2, GL_LINES,
                ('v2i', (int(x), int(y), vx, vy))
            )

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


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
