"""An interactive RCON shell."""

from argparse import ArgumentParser, Namespace
from logging import INFO, basicConfig, getLogger
from pathlib import Path

from rcon.config import CONFIG_FILES, LOG_FORMAT, from_args
from rcon.console import PROMPT, rconcmd
from rcon.errorhandler import ErrorHandler
from rcon.readline import CommandHistory


__all__ = ['get_args', 'main']


LOGGER = getLogger('rconshell')


def get_args() -> Namespace:
    """Parses and returns the CLI arguments."""

    parser = ArgumentParser(description='An interactive RCON shell.')
    parser.add_argument('server', nargs='?', help='the server to connect to')
    parser.add_argument('-c', '--config', type=Path, metavar='file',
                        default=CONFIG_FILES, help='the configuration file')
    parser.add_argument('-p', '--prompt', default=PROMPT, metavar='PS1',
                        help='the shell prompt')
    return parser.parse_args()


def main() -> None:
    """Runs the RCON shell."""

    args = get_args()
    basicConfig(level=INFO, format=LOG_FORMAT)

    if args.server:
        host, port, passwd = from_args(args)
    else:
        host = port = passwd = None

    with ErrorHandler(LOGGER):
        with CommandHistory(LOGGER):
            rconcmd(host, port, passwd, prompt=args.prompt)
