# rcon
An [RCON protocol](https://developer.valvesoftware.com/wiki/Source_RCON_Protocol) client implementation.

## Requirements
`rcon` requires Python 3.8 or higher.

## Documentation
[![Documentation Status](https://readthedocs.org/projects/rcon/badge/?version=latest)](https://rcon.readthedocs.io/en/latest/)  
Documentation is available on [readthedocs](https://rcon.readthedocs.io/en/latest/).

## Installations

Install rcon from the [AUR](https://aur.archlinux.org/packages/python-rcon/) or via:

    pip install rcon

## Quick start
The `RCON` protocol is used to remotely control a game server, i.e. execute
commands on a game server and receive the respective results.

```python
from rcon import Client

with Client('127.0.0.1', 5000, passwd='mysecretpassword') as client:
    response = client.run('some_command', 'with', 'some', 'arguments')

print(response)
```

## License
Copyright (C) 2018-2020 Richard Neumann <mail at richard dash neumann period de>

rcon is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

rcon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with rcon.  If not, see <http://www.gnu.org/licenses/>.
