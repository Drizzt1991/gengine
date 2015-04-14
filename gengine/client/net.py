import asyncio
import threading
import os
from gengine.protocol.packet import \
    parse as parse_packet, pack as pack_packet, OPCODES, get_channel
from collections import Counter

DEFAULT_PACKET_RETRY = 0.1
MAX_PACKET_TIMEOUT = 5


class NetProtocol:
    """ Simple game UDP protocol
    """

    def __init__(self, event_queue, *, loop):
        self.event_queue = event_queue
        self.loop = loop
        self.transport = None
        self._sequence_counters = Counter()
        self._ack_waiters = {}
        self._session_id = os.urandom(8)
        # If ACK did not arrive in this time, we will resend package
        self._retry_timout = DEFAULT_PACKET_RETRY

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print('Received %r from %s' % (data, addr))
        packet = parse_packet(data)
        # ACK should not propagate to application code
        if packet.opcode == OPCODES.ACK:
            waiter = self._ack_waiters.get(
                (packet.opcode, packet.ack_sequence_id))
            if waiter is not None:
                waiter.set_result(None)
                # Remove the future, so we will just ignore double ACK
                del self._ack_waiters[(packet.opcode, packet.ack_sequence_id)]
        else:
            self.packet_received(packet)

    def packet_received(self, packet):
        self.event_queue.put_nowait((packet))

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed")

    @asyncio.coroutine
    def send_packet(
            self, opcode, data, wait_ack=False,
            timeout=MAX_PACKET_TIMEOUT):
        channel_meta = get_channel(opcode)
        if not channel_meta.ack and wait_ack:
            raise ValueError("Can't use `wait_ack` for this channel")

        self._sequence_counters[channel_meta.channel_id] += 1
        sequence_id = self._sequence_counters[channel_meta.channel_id]
        send_time = self.loop.time()

        packed_packet = pack_packet(
            opcode,
            session_id=self._session_id,
            timestamp=send_time,
            sequence_id=sequence_id,
            **data)
        self.transport.sendto(packed_packet)

        if wait_ack:
            future = asyncio.Future(loop=self.loop)
            # Register waiter, so datagram_received could trigger it
            self._ack_waiters[(opcode, sequence_id)] = future
            try:
                while True:
                    # FIXME: We will round `timeout` to nearest retry cycle
                    #        currently. I see no problem with it though.
                    try:
                        yield from asyncio.wait_for(
                            future, self._retry_timout, loop=self.loop)
                    except asyncio.TimeoutError:
                        # If the timeout is too big resending is not an option
                        # any more
                        if (self.loop.time() - send_time) > timeout:
                            raise
                        # Resend the exact same package. If we receive 2 ACK
                        # it's not a problem
                        self.transport.sendto(packed_packet)
            finally:
                # Clean up after yourself if package could not be sent
                self._ack_waiters.pop((opcode, sequence_id), None)
                if not future.done():
                    future.cancel()


class NetThread(threading.Thread):

    def __init__(self, config, event_queue, *args, **kw):
        self.config = config
        self.event_queue = event_queue
        self.loop = asyncio.get_event_loop()
        self.__main_coroutine = asyncio.async(
            self.main_coroutine(), loop=self.loop)
        super().__init__(*args, **kw)

    def run(self):
        try:
            self.loop.run_until_complete(self.__main_coroutine)
            # Propagate any errors to stderr
            self.__main_coroutine.result()
        except asyncio.CancelledError:
            pass
        finally:
            self.loop.close()

    def stop(self):
        """ Will be run by main thread. Should be threadsafe
        """
        if self.is_alive():
            self.loop.call_soon_threadsafe(self.__stop)

    def __stop(self):
        self.__main_coroutine.cancel()

    # Main asyn net logic

    @asyncio.coroutine
    def main_coroutine(self):
        transport, protocol = yield from self.loop.create_datagram_endpoint(
            lambda self=self: NetProtocol(
                self.event_queue,
                loop=self.loop),
            remote_addr=(self.config['host'], self.config['port']))

        yield from protocol.send_packet(OPCODES.CONNECT, {}, wait_ack=True)
