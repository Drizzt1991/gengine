import asyncio
from unittest import TestCase


class AsyncTestCase(TestCase):

    def setUp(self):
        # We want explicit loops
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        if hasattr(self, "setUpCoroutine"):
            self.loop.run_until_complete(self.tearDownCoroutine())

    def tearDown(self):
        self.loop.stop()
        self.loop.close()
        if hasattr(self, "tearDownCoroutine"):
            self.loop.run_until_complete(self.tearDownCoroutine())
