Usage
=====
For usage in code, there is the class :py:class:`rcon.Client`.

.. code-block:: python

    from rcon import Client

    with Client('127.0.0.1', 5000, passwd='mysecretpassword') as client:
        response = client.run('some_command', 'with', 'some', 'arguments')

    print(response)

Async support
-------------
If you want to use RCOn in an asynchronous environment, use :py:func:`rcon.rcon`.

.. code-block:: python

    from rcon import rcon

    response = await rcon('some_command', 'with', 'some', 'arguments',
                          host='127.0.0.1', port=5000, passwd='mysecretpassword')
    print(response)

Configuration
-------------
`rconclt` servers can be configured in :file:`/etc/rcon.conf`.
The configuration file format is:

.. code-block:: ini

    [<server_name>]
    host = <hostname_or_ip_address>
    port = <port>
    passwd = <password>

The :code:`passwd` entry is optional.

rconclt
-------
`rconclt` is an RCON client script to communicate with game servers via the RCON protocol using the shell.
To communicate with a server, run:

.. code-block:: bash

    rconclt [options] <server> <command> [<args>...]

rconshell
---------
`rconshell` is an interactive RCON console to interact with game servers via the RCON protocol.
To start a shell, run:

.. code-block:: bash

    rconshell [server] [options]

Handling connection timeouts.
-----------------------------
You can specify an optional :code:`timeout=<sec>` parameter to allow a connection attempt to time out.
If a timeout is reached during a connection attempt, it will raise a `socket.timeout <https://docs.python.org/3/library/socket.html#socket.timeout>`_ exception.
The following example will raise a connection timeout after 1.5 seconds:

.. code-block:: python

    try:
        with Client('127.0.0.1', 5000, timeout=1.5) as client:
            <do_stuff>
    except socket.timeout as timeout:
        <handle_connection_timeout>

.. _configuration:
