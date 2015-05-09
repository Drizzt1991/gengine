import argparse
import pathlib
import time
from .world import World


def get_parser():
    parser = argparse.ArgumentParser(
        description='Asteroids game')
    # parser.add_argument(
    #     '--host', help='Host to connect to', default="localhost")
    # parser.add_argument(
    #     '--port', help='Port to connect to', default=24000, type=int)
    parser.add_argument(
        '--config', help='Path to config.ini', default="config.ini",
        type=pathlib.Path)
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    world = World()

    try:
        # We import here, so, that pyglet does not start before we parsed
        # arguments. This is useful if we ask for command line help to not
        # load GUI window.
        import pyglet
        from .window import GameWindow
        GameWindow(world, 600, 600)

        pyglet.app.run()
    except KeyboardInterrupt:
        print("Received SIG_INT. Quiting...")
