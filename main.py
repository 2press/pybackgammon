import argparse
import os
import socket

from app import App

os.environ['SDL_VIDEO_CENTERED'] = '1'


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Backgammon")
    parser.add_argument("--server", action="store_true")
    parser.add_argument(
        "--host", default=socket.gethostbyname(socket.gethostname()))
    parser.add_argument("--port", default='61096')
    args = parser.parse_args()
    theApp = App(args.host.strip(), int(args.port), args.server)
    theApp.on_execute()
