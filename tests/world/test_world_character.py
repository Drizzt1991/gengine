from unittest import mock
from gengine.testutil import AsyncTestCase
from gengine.world import World, Character
from gengine.vector import Vector2D


class TestWorldMovement(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.world = World(loop=self.loop)

    @mock.patch("gengine.world.World.notify")
    def test_character_load(self, patched):
        character = Character(
            character_id=1,
            initial_position=Vector2D(0, 0),
            initial_viewport=Vector2D(0, 1))
        # We have a static character in position (0, 0)
        load_time = 10
        self.world.load_character(character, timestamp=10)

        self.assertEqual(
            patched.call_count, 1,
            "`World.notify` was not called on character load")

        self.assertEqual(
            patched.call_args, ((), dict(
                affects=[character.character_id],
                event="character_load",
                character=character,
                timestamp=load_time
                )))

        # try to load another char and see, that both were notified about the
        # event
        another_character = Character(
            character_id=2,
            initial_position=Vector2D(0, 10),
            initial_viewport=Vector2D(0, 1))
        self.world.load_character(another_character, timestamp=10)

        self.assertEqual(
            patched.call_count, 2,
            "`World.notify` was not called on 2nd character load")

        self.assertEqual(
            patched.call_args, ((), dict(
                affects=[another_character.character_id,
                         character.character_id],
                event="character_load",
                character=character,
                timestamp=load_time
                )))

    def test_character_movement(self):
        character = Character(
            character_id=1,
            initial_position=Vector2D(0, 0),
            initial_viewport=Vector2D(0, 1))
        self.world.load_character(character, timestamp=0)
        character.update(
            velocity=Vector2D(1, 1),
            viewport=Vector2D.from_deg(45),
            timestamp=0)
        self.world.process_till(100)
        self.assertEqual(
            character.position,
            Vector2D(100, 100))
