import asyncio
from gengine.world.net.dispatcher import Dispatcher, ValidationError
from gengine.protocol.packet import \
    parse as packet_parse, get_channel, form_ack, pack as packet_pack, OPCODES


CONNECTION_TIMEOUT = 5


class NetProtocol:
    """ Simple UDP protocol for communication
    """

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print('Received %r from %s' % (data, addr))
        packet = packet_parse(data)
        if get_channel(packet.opcode).ack:
            self.transport.sendto(form_ack(packet), addr)
        try:
            self.dispatcher.feed(packet)
        except ValidationError as exc:
            self.transport.sendto(exc.pack(), addr)

    def error_received(self, exc):
        print('Error received:', exc)


class Connection:

    def __init__(self, net, character_id, session_id, *, loop):
        self.session_id = session_id
        self.character_id = character_id
        self.loop = loop
        self.net = net
        self.__connection_handle = None

    def start(self):
        self.__connection_handle = self.loop.call_later(
            CONNECTION_TIMEOUT, self._close_connection)

    def renew(self):
        self.__connection_handle.cancel()
        self.start()

    def _close_connection(self):
        self.net._connections.pop(self.session_id)

    def send_packet(self, opcode, data):
        channel_meta = get_channel(opcode)

        self._sequence_counters[channel_meta.channel_id] += 1
        sequence_id = self._sequence_counters[channel_meta.channel_id]

        packed_packet = packet_pack(
            opcode,
            session_id=self._session_id,
            sequence_id=sequence_id,
            **data)
        self.transport.sendto(packed_packet)


class Net:

    world = None

    def __init__(self, config,  *, loop):
        self.loop = loop
        self.config = config
        self.dispatcher = Dispatcher(self, loop=loop)
        self._server = None
        self.__main_coroutine = None
        self._connections = {}
        self._char_counter = 0

    def create_connection(self, session_id):
        self._char_counter += 1
        return Connection(
            net=self,
            character_id=self._char_counter,
            session_id=session_id,
            loop=self.loop)

    def start(self):
        self.__main_coroutine = asyncio.async(
            self.main_coroutine(), loop=self.loop)

    @asyncio.coroutine
    def main_coroutine(self):
        self._server = yield from self.loop.create_datagram_endpoint(
            lambda self=self: NetProtocol(self.dispatcher),
            local_addr=(self.config['host'], self.config['port']))

    def close(self):
        if self._server:
            self._server.close()

    def notify_character_login(self, character, timestamp):
        packet = packet_pack(
            OPCODES.CHAR_UPDATE,
            timestamp=timestamp,
            character_id=character.character_id,
            position_x=character.position.x,
            position_y=character.position.y,
            velocity_x=character.velocity.x,
            velocity_y=character.velocity.y,
            viewport_x=character.viewport.x,
            viewport_y=character.viewport.y,
            jump=0, rotation=0)
        for connection in self._connections.values():
            connection.send_packet(packet)
