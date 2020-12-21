"""An interactive console."""

from getpass import getpass
from typing import Union

from rcon.config import Config
from rcon.exceptions import RequestIdMismatch, WrongPassword
from rcon.proto import Client


__all__ = ['rconcmd']


EXIT_COMMANDS = {'exit', 'quit'}
MSG_QUERY_LATER = '\nOkay, I will ask again later.'
MSG_ABORTED = '\nAborted...'
MSG_LOGIN_ABORTED = '\nLogin aborted. Bye.'
MSG_EXIT = 'Bye.'
MSG_SESSION_TIMEOUT = 'Session timed out. Please login again.'
MSG_EXIT_USAGE = 'Usage: {} [<exit_code>].'
PROMPT = 'RCON> '


def read(prompt: str, typ: type = None) -> type:
    """Reads input and converts it to the respective type."""

    while True:
        raw = input(prompt)

        if typ is not None:
            try:
                return typ(raw)
            except (TypeError, ValueError):
                print(f'Invalid {typ}: {raw}')
                continue

        return raw


def read_or_none(prompt: str, typ: type = None) -> type:
    """Reads the input and returns None on EOFError."""

    try:
        return read(prompt, typ=typ)
    except EOFError:
        print(MSG_QUERY_LATER)
        return None


def login(client: Client, passwd: str) -> str:
    """Performs a login."""

    if passwd is None:
        passwd = getpass('Password: ')

    logged_in = False

    while not logged_in:
        try:
            logged_in = client.login(passwd)
        except WrongPassword:
            print('Invalid password.')
            passwd = getpass('Password: ')

    return passwd


def get_config(host: str, port: int, passwd: str) -> Config:
    """Reads the necessary arguments."""

    while any(item is None for item in (host, port, passwd)):
        if host is None:
            host = read_or_none('Host: ')

        if port is None:
            port = read_or_none('Port: ', typ=int)

        if passwd is None:
            passwd = read_or_none('Password: ')

    return Config(host, port, passwd)


def exit(exit_code: Union[int, str] = 0) -> int:    # pylint: disable=W0622
    """Exits the interactive shell via exit command."""

    print(MSG_EXIT)
    return int(exit_code)


def rconcmd(host: str, port: int, passwd: str, *, prompt: str = PROMPT) -> int:
    """Initializes the console."""

    try:
        config = get_config(host, port, passwd)
    except KeyboardInterrupt:
        print(MSG_ABORTED)
        return 1

    with Client(config.host, config.port) as client:
        try:
            passwd = login(client, config.passwd)
        except (EOFError, KeyboardInterrupt):
            print(MSG_LOGIN_ABORTED)
            return 1

        while True:
            try:
                command = input(prompt)
            except EOFError:
                print(f'\n{MSG_EXIT}')
                break
            except KeyboardInterrupt:
                print()
                continue

            try:
                command, *args = command.split()
            except ValueError:
                continue

            if command in EXIT_COMMANDS:
                try:
                    return exit(*args)  # pylint: disable=R1722
                except (TypeError, ValueError):
                    print(MSG_EXIT_USAGE.format(command))
                    continue

            try:
                result = client.run(command, *args)
            except RequestIdMismatch:
                print(MSG_SESSION_TIMEOUT)

                try:
                    passwd = login(client, passwd)
                except (EOFError, KeyboardInterrupt):
                    print(MSG_LOGIN_ABORTED)
                    return 2

            print(result)

    return 0
