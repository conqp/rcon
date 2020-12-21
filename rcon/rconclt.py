"""RCON client CLI."""

from argparse import ArgumentParser, Namespace
from getpass import getpass
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path
from socket import timeout
from sys import exit    # pylint: disable=W0622
from typing import Tuple

from rcon.errorhandler import ErrorHandler
from rcon.exceptions import InvalidConfig
from rcon.config import CONFIG_FILE, LOG_FORMAT, Config, servers
from rcon.exceptions import RequestIdMismatch, WrongPassword
from rcon.proto import Client


__all__ = ['get_credentials', 'main']


ERRORS = (
    (ConnectionRefusedError, 'Connection refused.', 3),
    (timeout, 'Connection timeout.', 4),
    (RequestIdMismatch, 'Unexpected request ID mismatch.', 5),
    (WrongPassword, 'Wrong password.', 6),
)
LOGGER = getLogger('rconclt')


def get_args() -> Namespace:
    """Parses and returns the CLI arguments."""

    parser = ArgumentParser(description='A Minecraft RCON client.')
    parser.add_argument('server', help='the server to connect to')
    parser.add_argument('-c', '--config', type=Path, metavar='file',
                        default=CONFIG_FILE, help='the configuration file')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print additional debug information')
    parser.add_argument('-t', '--timeout', type=float, metavar='seconds',
                        help='connection timeout in seconds')
    parser.add_argument('command', help='command to execute on the server')
    parser.add_argument('argument', nargs='*', default=(),
                        help='arguments for the command')
    return parser.parse_args()


def get_credentials(args: Namespace) -> Tuple[str, int, str]:
    """Get the credentials for a server from the respective server name."""

    try:
        host, port, passwd = Config.from_string(args.server)
    except InvalidConfig:
        try:
            host, port, passwd = servers(args.config)[args.server]
        except KeyError:
            LOGGER.error('No such server: %s.', args.server)
            exit(2)

    if passwd is None:
        try:
            passwd = getpass('Password: ')
        except (KeyboardInterrupt, EOFError):
            print()
            LOGGER.error('Aborted by user.')
            exit(1)

    return (host, port, passwd)


def main():
    """Runs the RCON client."""

    args = get_args()
    log_level = DEBUG if args.debug else INFO
    basicConfig(level=log_level, format=LOG_FORMAT)
    host, port, passwd = get_credentials(args)

    with ErrorHandler(ERRORS, LOGGER):
        with Client(host, port, timeout=args.timeout) as client:
            client.login(passwd)
            text = client.run(args.command, *args.argument)

    print(text, flush=True)
