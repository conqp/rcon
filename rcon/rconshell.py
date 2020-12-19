"""An interactive RCON shell."""

from argparse import ArgumentParser, Namespace
from logging import INFO, basicConfig, getLogger
from socket import timeout
from sys import exit    # pylint: disable=W0622

from rcon.rconclt import get_credentials
from rcon.console import rconcmd


__all__ = ['get_args', 'main']


LOGGER = getLogger('rconshell')
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'


def get_args() -> Namespace:
    """Parses and returns the CLI arguments."""

    parser = ArgumentParser(description='An interactive RCON shell.')
    parser.add_argument('server', nargs='?', help='the server to connect to')
    parser.add_argument('-p', '--prompt', default='RCON> ', metavar='PS1',
                        help='the shell prompt')
    return parser.parse_args()


def main():
    """Runs the RCON shell."""

    args = get_args()
    basicConfig(level=INFO, format=LOG_FORMAT)

    if server := args.server:
        host, port, passwd = get_credentials(server)
    else:
        host = port = passwd = None

    try:
        exit_code = rconcmd(host, port, passwd, args.prompt)
    except ConnectionRefusedError:
        LOGGER.error('Connection refused.')
        exit(3)
    except timeout:
        LOGGER.error('Connection timeout.')
        exit(4)

    exit(exit_code)
