"""GTK based GUI."""

from socket import timeout

from gi import require_version
require_version('Gtk', '3.0')
# pylint: disable=C0413
from gi.repository import Gtk

from rcon.exceptions import RequestIdMismatch, WrongPassword
from rcon.proto import Client


__all__ = ['main']


class GUI(Gtk.Window):
    """A GTK based GUI for RCON."""

    def __init__(self):
        """Initializes the GUI."""
        super().__init__(title='RCON GUI')

        self.set_position(Gtk.WindowPosition.CENTER)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.host = Gtk.Entry()
        self.host.set_placeholder_text('Host')
        self.grid.attach(self.host, 0, 0, 1, 1)

        self.port = Gtk.Entry()
        self.port.set_placeholder_text('Port')
        self.grid.attach(self.port, 1, 0, 1, 1)

        self.passwd = Gtk.Entry()
        self.passwd.set_placeholder_text('Password')
        self.grid.attach(self.passwd, 2, 0, 1, 1)

        self.command = Gtk.Entry()
        self.command.set_placeholder_text('Command')
        self.grid.attach(self.command, 0, 1, 2, 1)

        self.button = Gtk.Button(label='Run')
        self.button.connect('clicked', self.on_button_clicked)
        self.grid.attach(self.button, 2, 1, 1, 1)

        self.result = Gtk.Entry()
        self.result.set_placeholder_text('Result')
        self.grid.attach(self.result, 0, 2, 3, 1)

    def show_error(self, message: str):
        """Shows an error message."""
        message_dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message)
        message_dialog.run()
        message_dialog.destroy()

    def on_button_clicked(self, _):
        """Runs the client."""
        if not (host := self.host.get_text()):  # pylint: disable=C0325
            self.show_error('No host specified.')
            return

        if not (port := self.port.get_text()):  # pylint: disable=C0325
            self.show_error('No port specified.')
            return

        try:
            port = int(port)
        except ValueError:
            self.show_error(f'Invalid port: {port}')
            return

        passwd = self.passwd.get_text()

        if not (command := self.command.get_text()):    # pylint: disable=C0325
            self.show_error('No command entered.')
            return

        try:
            with Client(host, port, passwd=passwd) as client:
                result = client.run(command)
        except ConnectionRefusedError:
            self.show_error('Connection refused.')
        except timeout:
            self.show_error('Connection timed out.')
        except RequestIdMismatch:
            self.show_error('Request ID mismatch.')
        except WrongPassword:
            self.show_error('Invalid password.')
        else:
            self.result.set_text(result)


def main():
    """Starts the GUI."""

    win = GUI()
    win.connect('destroy', Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
