

from gengine.protocol import ReliableProtocol


class WorldHubProtocol(ReliableProtocol):

    def __init__(self, dispatcher, *, loop):
        self.dispatcher = dispatcher
        self.loop = loop

    def packet_received(self, packet):
        self.dispatcher.feed_raw(packet)
