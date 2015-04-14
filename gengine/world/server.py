import argparse
import asyncio
from gengine.world.net import Net
from gengine.world.world import World


def get_parser():
    parser = argparse.ArgumentParser(
        description='Gengine server')
    parser.add_argument(
        '--host', help='Host to listen on', default="localhost")
    parser.add_argument(
        '--port', help='Port to listen on', default=24000, type=int)
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    net = Net(vars(args), loop=loop)
    world = World(net=net, loop=loop)
    net.world = world
    net.start()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        net.close()
        # world.close()

if __name__ == "__main__":
    main()
