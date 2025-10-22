from __future__ import annotations, print_function

import errno
import socket

from navel._pyproto import klframe_pb2 as _klframe

# Buffer size of socket; warning required size scales linearly with people
# detected
_SC_SOCK_BUF = 1024 * 10


class ProtobufSocket(object):
    """Creates an object which can transceive protobuf messages via UDS.

    Args:
        socket_name (str): Name of socket to connect to.
    """

    def __init__(self, socket_name):
        self._sock = 0
        self._socket_name = socket_name

        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self, attempts=1):
        """Connects object to its Unix domain socket.

        Will attempt to connect to UDS set at object creation. If the
        attempts argument is passed and connection fails, this method will
        loop multiple times to reconnect.

        Args:
            attempts (int, optional): How many attempts should be made to
                connect. Defaults to 1.
        Raises:
            ConnectionError: If unable to connect.
        """

        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)

        for i in range(attempts):
            try:
                self._sock.connect(self._socket_name)
                return

            except OSError as err:
                if err.errno == errno.EISCONN:
                    return
                if i == attempts - 1:
                    msg = f"Failed to connect to {self._socket_name}"
                    raise ConnectionError(msg) from err

    def disconnect(self):
        """Disconnects socket."""

        self._sock.close()

    def send(self, data, ptype):
        msg = _klframe.Klframe()
        msg.data = data.SerializeToString()
        msg.ptype = ptype
        msg = msg.SerializeToString()

        self._sock.sendall(msg)

    def recv(self):
        data = self._sock.recv(_SC_SOCK_BUF, socket.MSG_DONTWAIT)

        if data:
            msg = _klframe.Klframe()
            msg.ParseFromString(data)
            return msg
