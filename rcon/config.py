"""RCON server configuration."""

from __future__ import annotations
from configparser import ConfigParser, SectionProxy
from logging import getLogger
from os import getenv, name
from pathlib import Path
from typing import Dict, Iterator, NamedTuple, Tuple


__all__ = ['CONFIG_FILE', 'LOG_FORMAT', 'Config', 'servers']


CONFIG = ConfigParser()

if name == 'posix':
    CONFIG_FILE = Path('/etc/rcon.conf')
elif name == 'nt':
    CONFIG_FILE = Path(getenv('LOCALAPPDATA')).joinpath('rcon.conf')
else:
    raise NotImplementedError(f'Unsupported operating system: {name}')

LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger('RCON Config')


class Config(NamedTuple):
    """Represents server configuration."""

    host: str
    port: int
    passwd: str = None

    @classmethod
    def from_string(cls, string: str) -> Config:
        """Reads the credentials from the given string."""
        try:
            host, port = string.split(':')
        except ValueError:
            raise ValueError(f'Invalid socket: {string}.') from None

        port = int(port)

        try:
            passwd, host = host.rsplit('@', maxsplit=1)
        except ValueError:
            passwd = None

        return cls(host, port, passwd)

    @classmethod
    def from_config_section(cls, section: SectionProxy) -> Config:
        """Creates a credentials tuple from
        the respective config section.
        """
        host = section['host']
        port = section.getint('port')
        passwd = section.get('passwd')
        return cls(host, port, passwd)


def entries(config_parser: ConfigParser) -> Iterator[Tuple[str, Config]]:
    """Yields entries."""

    for section in config_parser.sections():
        yield (section, Config.from_config_section(config_parser[section]))


def servers(config_file: Path = CONFIG_FILE) -> Dict[str, Config]:
    """Returns a dictionary of servers."""

    CONFIG.read(config_file)
    return dict(entries(CONFIG))
