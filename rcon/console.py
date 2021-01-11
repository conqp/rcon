"""An interactive console."""

from getpass import getpass

from rcon.client import Client
from rcon.config import Config
from rcon.exceptions import RequestIdMismatch, WrongPassword


__all__ = ['rconcmd']


EXIT_COMMANDS = {'exit', 'quit'}
MSG_LOGIN_ABORTED = '\nLogin aborted. Bye.'
MSG_EXIT = '\nBye.'
MSG_SESSION_TIMEOUT = 'Session timed out. Please login again.'
PROMPT = 'RCON {host}:{port}> '


def read_host() -> str:
    """Reads the host."""

    while True:
        try:
            return input('Host: ')
        except KeyboardInterrupt:
            print()
            continue


def read_port() -> int:
    """Reads the port."""

    while True:
        try:
            port = input('Port: ')
        except KeyboardInterrupt:
            print()
            continue

        try:
            port = int(port)
        except ValueError:
            print(f'Invalid integer: {port}')
            continue

        if 0 <= port <= 65535:
            return port

        print(f'Invalid port: {port}')


def read_passwd() -> str:
    """Reads the password."""

    while True:
        try:
            return getpass('Password: ')
        except KeyboardInterrupt:
            print()


def get_config(host: str, port: int, passwd: str) -> Config:
    """Reads the necessary arguments."""

    if host is None:
        host = read_host()

    if port is None:
        port = read_port()

    if passwd is None:
        passwd = read_passwd()

    return Config(host, port, passwd)


def login(client: Client, passwd: str) -> str:
    """Performs a login."""

    while True:
        try:
            client.login(passwd)
        except WrongPassword:
            print('Wrong password.')
            passwd = read_passwd()
            continue

        return passwd


def process_input(client: Client, passwd: str, prompt: str) -> bool:
    """Processes the CLI input."""

    try:
        command = input(prompt)
    except KeyboardInterrupt:
        print()
        return True
    except EOFError:
        print(MSG_EXIT)
        return False

    try:
        command, *args = command.split()
    except ValueError:
        return True

    if command in EXIT_COMMANDS:
        return False

    try:
        result = client.run(command, *args)
    except RequestIdMismatch:
        print(MSG_SESSION_TIMEOUT)

        try:
            passwd = login(client, passwd)
        except EOFError:
            print(MSG_LOGIN_ABORTED)
            return False

    print(result)
    return True


def rconcmd(host: str, port: int, passwd: str, *, prompt: str = PROMPT):
    """Initializes the console."""

    try:
        host, port, passwd = get_config(host, port, passwd)
    except EOFError:
        print(MSG_EXIT)
        return

    prompt = prompt.format(host=host, port=port)

    with Client(host, port) as client:
        try:
            passwd = login(client, passwd)
        except EOFError:
            print(MSG_LOGIN_ABORTED)
            return

        while True:
            if not process_input(client, passwd, prompt):
                break
