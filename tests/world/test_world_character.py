import asyncio
from unittest import mock
from gengine.testutil import AsyncTestCase
from gengine.world import World, Character
from gengine.vector import Vector2D


class TestWorldMovement(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.world = World(loop=self.loop, timestamp=0)

    def tearDown(self):
        self.world.close()

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
            tuple(patched.call_args), ((), dict(
                affects=[character],
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
            tuple(patched.call_args), ((), dict(
                affects=[another_character,
                         character],
                event="character_load",
                character=another_character,
                timestamp=load_time
                )))

    @mock.patch("gengine.world.World.notify")
    def test_character_passive_movement(self, patched):
        character = Character(
            character_id=1,
            initial_position=Vector2D(0, 0),
            initial_viewport=Vector2D(0, 1))
        self.world.load_character(character, timestamp=0)

        self.world.update_character(
            character,
            velocity=Vector2D(1, 1),
            viewport=Vector2D.from_deg(45),
            timestamp=0)

        self.loop.run_until_complete(asyncio.sleep(0.1, loop=self.loop))

        self.assertEqual(
            patched.call_count, 2,
            "`World.notify` was not called on character passive move")

        self.assertEqual(
            tuple(patched.call_args), ((), dict(
                affects=[character],
                event="character_move",
                character=character,
                timestamp=0
                )))

        self.loop.run_until_complete(asyncio.sleep(1, loop=self.loop))
        self.assertEqual(
            patched.call_count, 3,
            "`World.notify` was not called on character passive move")

        self.assertEqual(
            tuple(patched.call_args), ((), dict(
                affects=[character],
                event="character_move",
                character=character,
                timestamp=1
                )))
        self.assertEqual(
            character.position,
            Vector2D(1, 1))
