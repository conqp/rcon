[![Documentation Status](https://readthedocs.org/projects/rcon/badge/?version=latest)](https://rcon.readthedocs.io/en/latest/)

# rcon
An RCON client implementation.
* [Source RCON protocol](https://developer.valvesoftware.com/wiki/Source_RCON_Protocol)
* [BattlEye RCon protocol](https://www.battleye.com/downloads/BERConProtocol.txt)

## Requirements
`rcon` requires Python 3.10 or higher.

## Documentation
Documentation is available on [readthedocs](https://rcon.readthedocs.io/en/latest/).

## Installation
Install rcon from the [AUR](https://aur.archlinux.org/packages/python-rcon/) or via:

    pip install rcon

## Quick start
The `RCON` protocols are used to remotely control game servers, i.e. execute
commands on a game server and receive the respective results.

### Source RCON
```python
from rcon.source import Client

with Client('127.0.0.1', 5000, passwd='mysecretpassword') as client:
    response = client.run('some_command', 'with', 'some', 'arguments')

print(response)
```

#### Async support
If you prefer to use Source RCON in an asynchronous environment, you can use 
`rcon()`.

```python
from rcon.source import rcon

response = await rcon(
    'some_command', 'with', 'some', 'arguments',
    host='127.0.0.1', port=5000, passwd='mysecretpassword'
)
print(response)
```

### BattlEye RCon
```python
from rcon.battleye import Client

with Client('127.0.0.1', 5000, passwd='mysecretpassword') as client:
    response = client.run('some_command', 'with', 'some', 'arguments')

print(response)
```

#### Handling server messages
Since the BattlEye RCon server will also send server messages to the client 
alongside command responses, you can register an event handler to process 
those messages:

```python
from rcon.battleye import Client
from rcon.battleye.proto import ServerMessage

def my_message_handler(server_message: ServerMessage) -> None:
    """Print server messages."""
    
    print('Server message:', server_message)

with Client(
        '127.0.0.1',
        5000,
        passwd='mysecretpassword',
        message_handler=my_message_handler
) as client:
    response = client.run('some_command', 'with', 'some', 'arguments')

print('Response:', response)
```

Have a look at `rcon.battleye.proto.ServerMessage` for details on the 
respective objects.
