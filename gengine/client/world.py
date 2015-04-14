from gengine.vector import Vector2D


class CharacterView:

    def __init__(self, position, viewport):
        self.position = position
        self.viewport = viewport

    def update(self, position=None, viewport=None):
        if position:
            self.position = position
        if viewport:
            self.viewport = viewport


class WorldView:

    def __init__(self):
        self._characters = [
            CharacterView(Vector2D(200, 200), Vector2D(0, 0))
        ]
