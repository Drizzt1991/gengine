import asyncio
# from gengine.world.character import Character
from gengine.world.shape import SimpleObjectIndex
from heapq import heappop, heappush
# from gengine.vector import Vec2

NEARBY_RADIUS = 20
COMPONENT_SCHEDULE_AHEAD = 1
SCHEDULE_DELTA = 0.01


class Event:

    def __init__(self, id, character, predicted_position):
        self._cancelled = False
        self.id = id
        self.character = character
        self.predicted_position = predicted_position


class EventHandle(float):

    __slots__ = ["_meta"]

    def __new__(cls, *args, **kw):
        meta = kw.pop("meta")
        obj = super().__new__(cls, *args, **kw)
        obj._meta = meta
        return obj

    def __repr__(self):
        return 'EventHandle({}, meta={!r})>'.format(
            super().__repr__(), self._meta)

    @property
    def timestamp(self):
        return float(self)

    def cancel(self):
        self._meta._cancelled = True


class WorldStateMachine:

    def __init__(self, timestamp):
        self._object_index = SimpleObjectIndex()
        self._events = []
        self._character_next_event = {}
        self._simulator = self._simulator_gen()
        next(self._simulator)  # Move to first yield so we can send time's
        self._current_time = timestamp
        self._subscribers = []

    def time(self):
        return self._current_time

    def _simulator_gen(self):
        """ Generator, that processes all events in events list
        """
        while True:
            # remove cancelled
            if self._events:
                while self._events[0]._meta._cancelled:
                    heappop(self._events)

            new_time = yield

            # Passing None just forces processor to run 1 passive loop
            # Can be used to clean cancelled
            if new_time is not None:
                self._current_time = new_time

            while self._events[0].timestamp <= self._current_time:
                event = heappop(self._events)
                event_meta = event._meta
                if event_meta._cancelled:
                    continue
                event_timestamp = event.timestamp
                if event_meta.id == "reschedule_character":
                    # Update last predicted position
                    character = event_meta.character
                    character.position = event_meta.predicted_position
                    character.timestamp = event_timestamp
                    self._reschedule_character(character, event_timestamp)
                    # Notify subscribers
                    affected = self._object_index.get_nearest_objects(
                        character.position, NEARBY_RADIUS)
                    self._notify(
                        event="character_move",
                        affects=affected,
                        character=character,
                        timestamp=event_timestamp)

    def _reschedule_character(self, character, timestamp):
        assert character.timestamp == timestamp
        # Predict new movement
        reschedule_time = timestamp + COMPONENT_SCHEDULE_AHEAD
        predicted_position = character.position_at(reschedule_time)

        # Find first pending collision and process it
        collisions = self._object_index.get_collisions(
            character.position, timestamp, predicted_position, reschedule_time)
        assert not collisions

        # FIXME: Unschedule old collision events, notify if needed

        # FIXME: Schedule collision instead of reschedule event

        self._object_index.update_character(character)

        last_handle = self._character_next_event.get(character.character_id)
        if last_handle is not None:
            last_handle.cancel()

        # If none just set update to be done in COMPONENT_SCHEDULE_AHEAD sec
        handle = EventHandle(
            reschedule_time,
            meta=Event("reschedule_character", character, predicted_position))
        heappush(self._events, handle)
        self._character_next_event[character.character_id] = handle
        return handle is self._events[0]

    def load_character(self, character, timestamp):
        # Bind character to this world
        character._world = self
        character.timestamp = timestamp

        # FIXME: Handle loading collisions

        # Add character to listeners
        upfront = self._reschedule_character(character, timestamp)

        # Notify subscribers
        affected = self._object_index.get_nearest_objects(
            character.position, NEARBY_RADIUS)
        self._notify(
            event="character_load",
            affects=affected,
            character=character,
            timestamp=timestamp)
        return upfront

    def update_character(self, character, timestamp, **update_data):
        # We may have received same velocities, so nothing to reschedule
        if not character.changes(**update_data):
            return
        # Move character to new spot
        new_position = character.position_at(timestamp)
        character.position = new_position
        character.timestamp = timestamp
        # Update velocities
        character.update(timestamp=timestamp, **update_data)
        # Update character movement in event scheduler
        upfront = self._reschedule_character(character, timestamp)

        # Notify subscribes
        affected = self._object_index.get_nearest_objects(
            character.position, NEARBY_RADIUS)
        self._notify(
            event="character_move",
            affects=affected,
            character=character,
            timestamp=timestamp)
        return upfront

    def unload_character(self):
        pass

    def _notify(self, *, event, affects, timestamp, **event_data):
        for notifier in self._subscribers:
            notifier.notify(
                event=event, affects=affects, timestamp=timestamp,
                **event_data)

    def subscribe(self, notifier):
        self._subscribers.append(notifier)

    def next_event_at(self):
        if not self._events:
            return None
        return self._events[0].timestamp

    def simulate_til(self, timestamp):
        if not self._events:
            return
        self._simulator.send(timestamp)


class World:

    def __init__(self, *, timestamp, loop):
        self._loop = loop
        self._object_index = SimpleObjectIndex()
        self._events = []
        self._event_waiter = None
        self._processing_task = asyncio.async(
            self._world_processor(), loop=loop)
        self._state_machine = WorldStateMachine(timestamp)
        self._state_machine.subscribe(self)
        self._time_diff = timestamp - loop.time()

    def time(self):
        return self._loop.time() + self._time_diff

    def _wake_scheduler_up(self):
        if self._event_waiter and not self._event_waiter.done():
            self._event_waiter.set_result(None)

    @asyncio.coroutine
    def _wait_until(self, event_timestamp):
        if event_timestamp is not None:
            current_time = self.time()

            if current_time > event_timestamp:
                return
            dt = event_timestamp - current_time
        else:
            dt = None
        self._event_waiter = asyncio.Future(loop=self._loop)
        try:
            yield from asyncio.wait_for(
                self._event_waiter, timeout=dt, loop=self._loop)
        except asyncio.TimeoutError:
            pass
        finally:
            self._event_waiter = None

    @asyncio.coroutine
    def _world_processor(self):
        while True:
            event_timestamp = self._state_machine.next_event_at()
            yield from self._wait_until(event_timestamp)
            current_time = self.time()
            self._state_machine.simulate_til(current_time)

    def close(self):
        self._processing_task.cancel()
        self._processing_task = None

    def load_character(self, character, timestamp):
        reschedule_needed = self._state_machine.load_character(
            character, timestamp)
        if reschedule_needed:
            self._wake_scheduler_up()

    def update_character(self, character, timestamp, **update_data):
        reschedule_needed = self._state_machine.update_character(
            character, timestamp, **update_data)
        if reschedule_needed:
            self._wake_scheduler_up()

    def notify(self, *, event, affects, timestamp, **event_data):
        pass
