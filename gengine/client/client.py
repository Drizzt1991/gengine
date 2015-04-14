import argparse
from queue import Queue

from .world import WorldView
from .net import NetThread


def get_parser():
    parser = argparse.ArgumentParser(
        description='Gengine client')
    parser.add_argument(
        '--host', help='Host to connect to', default="localhost")
    parser.add_argument(
        '--port', help='Port to connect to', default=24000, type=int)
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    worldview = WorldView()
    event_queue = Queue()
    net_thread = NetThread(vars(args), event_queue)
    net_thread.start()

    try:
        # We import here, so, that pyglet does not start before we parsed
        # arguments. This is useful if we ask for command line help to not
        # load GUI window.
        import pyglet
        from .window import GameWindow
        GameWindow(worldview, event_queue)

        pyglet.app.run()
    except KeyboardInterrupt:
        print("Received SIG_INT. Quiting...")
    finally:
        net_thread.stop()
        net_thread.join()


if __name__ == "__main__":
    main()
