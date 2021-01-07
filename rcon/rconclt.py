"""RCON client CLI."""

from argparse import ArgumentParser, Namespace
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path

from rcon.errorhandler import ErrorHandler
from rcon.config import CONFIG_FILES, LOG_FORMAT, from_args
from rcon.proto import Client


__all__ = ['main']


LOGGER = getLogger('rconclt')


def get_args() -> Namespace:
    """Parses and returns the CLI arguments."""

    parser = ArgumentParser(description='A Minecraft RCON client.')
    parser.add_argument('server', help='the server to connect to')
    parser.add_argument('-c', '--config', type=Path, metavar='file',
                        default=CONFIG_FILES, help='the configuration file')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print additional debug information')
    parser.add_argument('-t', '--timeout', type=float, metavar='seconds',
                        help='connection timeout in seconds')
    parser.add_argument('command', help='command to execute on the server')
    parser.add_argument('argument', nargs='*', default=(),
                        help='arguments for the command')
    return parser.parse_args()


def main() -> None:
    """Runs the RCON client."""

    args = get_args()
    basicConfig(format=LOG_FORMAT, level=DEBUG if args.debug else INFO)
    host, port, passwd = from_args(args)

    with ErrorHandler(LOGGER):
        with Client(host, port, timeout=args.timeout) as client:
            client.login(passwd)
            text = client.run(args.command, *args.argument)

    print(text, flush=True)
