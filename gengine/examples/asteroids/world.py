import math
import random
from functools import partial
from heapq import heappop, heappush
from planar import Vec2, EPSILON

from .components import SpaceShip, Asteroid, Bullet


class EventHandle(float):

    __slots__ = ["_meta", "_cancelled"]

    def __new__(cls, *args, **kw):
        meta = kw.pop("meta")
        obj = super().__new__(cls, *args, **kw)
        obj._meta = meta
        obj._cancelled = False
        return obj

    def __repr__(self):
        return 'EventHandle({}, meta={!r})>'.format(
            super().__repr__(), self._meta)

    @property
    def timestamp(self):
        return float(self)

    def cancel(self):
        self._cancelled = True


class BaseWorld:

    def __init__(self, timestamp, width, height):
        self._events = []
        self._character_next_event = {}
        self._simulator = self._simulator_gen()
        next(self._simulator)  # Move to first yield so we can send time's
        self._current_time = timestamp
        self._subscribers = []
        self.width, self.height = width, height

    def time(self):
        return self._current_time

    def _simulator_gen(self):
        """ Generator, that processes all events in events list
        """
        while True:
            # remove cancelled
            if self._events:
                while self._events[0]._cancelled:
                    heappop(self._events)

            new_time = yield

            # Passing None just forces processor to run 1 passive loop
            # Can be used to clean cancelled
            if new_time is not None:
                self._current_time = new_time

            while self._events and \
                    self._events[0].timestamp <= self._current_time:
                event = heappop(self._events)
                if event._cancelled:
                    continue
                event_meta = event._meta
                self._process_event(event_meta, event.timestamp)

    def _notify(self, *, event, affects, timestamp, **event_data):
        for notifier in self._subscribers:
            notifier.notify(
                event=event, affects=affects, timestamp=timestamp,
                **event_data)

    def _process_event(self, event, timestamp):
        raise NotImplementedError

    def _schedule_event(self, event, timestamp):
        heappush(self._events, EventHandle(timestamp, meta=event))

    # Open interface

    def subscribe(self, notifier):
        self._subscribers.append(notifier)

    def next_event_at(self):
        if not self._events:
            return None
        return self._events[0].timestamp

    def simulate_til(self, timestamp):
        assert self._current_time < timestamp
        self._simulator.send(timestamp)

    def advance_by(self, dt):
        new_timestamp = self._current_time + dt
        self._simulator.send(new_timestamp)


class World(BaseWorld):

    MAX_BULLETS = 1
    ASTEROID_SPEED_MIN = 5
    ASTEROID_SPEED_MAX = 20

    def _process_event(self, event, timestamp):
        event(timestamp)

    # def _reschedule_character(self, character, timestamp):
    #     assert character.timestamp == timestamp
    #     # Predict new movement
    #     reschedule_time = timestamp + COMPONENT_SCHEDULE_AHEAD
    #     predicted_position = character.position_at(reschedule_time)

    #     # Find first pending collision and process it
    #     collisions = self._object_index.get_collisions(
    #         character.position, timestamp, predicted_position, reschedule_time)
    #     assert not collisions

    #     # FIXME: Unschedule old collision events, notify if needed

    #     # FIXME: Schedule collision instead of reschedule event

    #     self._object_index.update_character(character)

    #     last_handle = self._character_next_event.get(character.character_id)
    #     if last_handle is not None:
    #         last_handle.cancel()

    #     # If none just set update to be done in COMPONENT_SCHEDULE_AHEAD sec
    #     handle = EventHandle(
    #         reschedule_time,
    #         meta=Event("reschedule_character", character, predicted_position))
    #     heappush(self._events, handle)
    #     self._character_next_event[character.character_id] = handle
    #     return handle is self._events[0]

    # def load_character(self, character, timestamp):
    #     # Bind character to this world
    #     character._world = self
    #     character.timestamp = timestamp

    #     # FIXME: Handle loading collisions

    #     # Add character to listeners
    #     upfront = self._reschedule_character(character, timestamp)

    #     # Notify subscribers
    #     affected = self._object_index.get_nearest_objects(
    #         character.position, NEARBY_RADIUS)
    #     self._notify(
    #         event="character_load",
    #         affects=affected,
    #         character=character,
    #         timestamp=timestamp)
    #     return upfront

    # def update_character(self, character, timestamp, **update_data):
    #     # We may have received same velocities, so nothing to reschedule
    #     if not character.changes(**update_data):
    #         return
    #     # Move character to new spot
    #     new_position = character.position_at(timestamp)
    #     character.position = new_position
    #     character.timestamp = timestamp
    #     # Update velocities
    #     character.update(timestamp=timestamp, **update_data)
    #     # Update character movement in event scheduler
    #     upfront = self._reschedule_character(character, timestamp)

    #     # Notify subscribes
    #     affected = self._object_index.get_nearest_objects(
    #         character.position, NEARBY_RADIUS)
    #     self._notify(
    #         event="character_move",
    #         affects=affected,
    #         character=character,
    #         timestamp=timestamp)
    #     return upfront

    # def unload_character(self):
    #     pass

    def __init__(self, timestamp=0):
        super().__init__(timestamp, 100, 100)
        self._objects = [
        ]
        self._spawn_player(timestamp)
        self._spawn_asteroids(timestamp, 10)
        self._bullet_count = 0  # Will be used to limit count of bullets

    def _clip_position(self, position):
        pos_x, pos_y = position
        if math.fabs(math.fabs(pos_x) - self.width / 2) < EPSILON:
            if pos_x > 0:
                pos_x -= self.width
            else:
                pos_x += self.width
        if math.fabs(math.fabs(pos_y) - self.height / 2) < EPSILON:
            if pos_y > 0:
                pos_y -= self.height
            else:
                pos_y += self.height
        return Vec2(pos_x, pos_y)

    def _spawn_asteroids(self, timestamp, asteroid_count):
        for i in range(asteroid_count):
            position = Vec2(random.randint(-self.width/2, self.width/2),
                            random.randint(-self.height/2, self.height/2))
            position = position * 0.9
            angle = random.randint(0, 360)
            speed = random.randint(
                self.ASTEROID_SPEED_MIN, self.ASTEROID_SPEED_MAX)
            velocity = Vec2.polar(angle, speed)
            ast = Asteroid(position, velocity, timestamp)
            self._add_asteroid(timestamp, ast)

    def _spawn_player(self, timestamp):
        self.player = SpaceShip(
            Vec2(0, 0), Vec2(0, 0), 90, timestamp)
        self.player._world = self
        self._objects.append(self.player)

    def _add_asteroid(self, timestamp, asteroid):
        asteroid._world = self
        self._objects.append(asteroid)
        # Schedule portal when object leaves bounds
        # FIXME: Use ray tracing technique to 2 planes
        vel_x, vel_y = asteroid._velocity
        pos_x, pos_y = asteroid._position
        times = []
        # Can not divide by 0
        if math.fabs(vel_x) > EPSILON:
            if vel_x < 0:
                bound = -self.width/2
            else:
                bound = self.width/2
            times.append(-(pos_x - bound) / vel_x)
        if math.fabs(vel_y) > EPSILON:
            if vel_y < 0:
                bound = -self.height/2
            else:
                bound = self.height/2
            times.append(-(pos_y - bound) / vel_y)
        dt = min(times)
        assert dt > 0, str((dt, vel_x, vel_y, pos_x, pos_y))
        self._schedule_event(
            partial(self._port_asteroid, asteroid=asteroid), timestamp+dt)

    def _remove_asteroid(self, timestamp, asteroid):
        asteroid._world = None
        try:
            self._objects.remove(asteroid)
        except ValueError:
            pass
            # FIXME: Should be fixed. If 2 bullets launched in the same time
            #        we should not schedule _split but rather collision and
            #        reindex collisions uppon asteroid removal

    def _split_asteroid(self, timestamp, asteroid):
        self._remove_asteroid(timestamp, asteroid)

    def _port_asteroid(self, timestamp, asteroid):
        asteroid._update_time(timestamp)
        self._remove_asteroid(timestamp, asteroid)
        asteroid._position = self._clip_position(asteroid.position)
        self._add_asteroid(timestamp, asteroid)

    def _check_collision_bullet(self, timestamp, bullet):
        collisions = []
        for obj in self._objects:
            if not isinstance(obj, Asteroid):
                continue
            # Check collision Asteroid to bullet
            obj._update_time(timestamp)
            s = bullet.position - obj.position  # Distance between centers
            v = bullet._velocity - obj._velocity  # Relative motion
            r = bullet.radius - obj.radius  # Sum of radii
            c = s.dot(s) - r * r
            if c < 0.0:
                dt = 0
            else:
                a = v.dot(v)
                if a < EPSILON:
                    # Not intersecting. Not moving relative to each other
                    continue
                b = v.dot(s)
                if b >= 0:
                    # Not intersecting. Moving in oposite or parallel
                    continue
                d = b * b - a * c  # Denominant for movement equation
                if d < 0:
                    # Spheres dont intersect. No real roots of equation
                    continue
                dt = (-b - math.sqrt(d)) / a
            collisions.append((dt, obj))
        if collisions:
            return min(collisions, key=lambda x: x[0])
        return None

    def _add_bullet(self, timestamp, bullet):
        # Ignore if we have too much bullets in world already
        if self._bullet_count >= self.MAX_BULLETS:
            return
        bullet._world = self
        self._objects.append(bullet)
        self._bullet_count += 1

        ttl = bullet.ttl
        collision = self._check_collision_bullet(timestamp, bullet)
        if collision:
            dt, asteroid = collision
            if dt < ttl:
                # Remove bullet earlier, cause it hit asteroid
                ttl = dt
                # Split asteroid
                self._schedule_event(
                    partial(self._split_asteroid, asteroid=asteroid),
                    timestamp+ttl)

        # Schedule port of bullets
        vel_x, vel_y = bullet._velocity
        pos_x, pos_y = bullet._position
        times = []
        # Can not divide by 0
        if math.fabs(vel_x) > EPSILON:
            if vel_x < 0:
                bound = -self.width/2
            else:
                bound = self.width/2
            times.append(-(pos_x - bound) / vel_x)
        if math.fabs(vel_y) > EPSILON:
            if vel_y < 0:
                bound = -self.height/2
            else:
                bound = self.height/2
            times.append(-(pos_y - bound) / vel_y)
        port_dt = min(times)
        assert port_dt > 0, str((port_dt, vel_x, vel_y, pos_x, pos_y))
        if port_dt < ttl:
            self._schedule_event(
                partial(self._port_bullet, bullet=bullet), timestamp+port_dt)
        else:
            self._schedule_event(
                partial(self._remove_bullet, bullet=bullet), timestamp+ttl)

    def _remove_bullet(self, timestamp, bullet):
        bullet._world = None
        self._objects.remove(bullet)
        self._bullet_count -= 1

    def _port_bullet(self, timestamp, bullet):
        bullet.ttl -= timestamp - bullet._timestamp
        bullet._update_time(timestamp)
        self._remove_bullet(timestamp, bullet)
        bullet._position = self._clip_position(bullet.position)
        bullet._timestamp = timestamp
        self._add_bullet(timestamp, bullet)
