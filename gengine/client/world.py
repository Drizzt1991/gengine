from planar import Vec2


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
            CharacterView(Vec2(200, 200), Vec2(0, 0))
        ]
