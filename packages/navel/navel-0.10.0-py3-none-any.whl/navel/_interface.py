import asyncio
from warnings import warn

import alsaaudio

from navel import _messages
from navel._async import AsyncRunner

NAVEL_MOTION_SOCKET = "/run/bodyd/motion.sock"
NAVEL_MOTION_RX_SOCKET = (
    "/run/bodyd/motion_tx.sock"  # FIXME: remove temporary workaround
)
NAVEL_PERCEPTION_SOCKET = "/run/bodyd/vision.sock"
NAVEL_SPEECH_SOCKET = "/run/bodyd/speech.sock"

MVC1_VOL_MAX = 16000  # Tegra specific max volume
MVC1_VOL_LIMIT = 0.8  # Relative to MVC1_VOL_MAX


class Motion(_messages.MotionMessenger):
    """Send messages to motion socket.

    This class is able to send protobuf messages via a unix
    domain socket (UDS). As soon as the object is created it will
    attempt to connect to the socket. If socket connection is successful,
    methods can be used to send messages. Each message is  converted
    to a protobuf format before being sent to the motion socket.

    Args:
        socket_name (str): Name of motion socket to connect too.
    """

    def __init__(
        self,
        socket_name=NAVEL_MOTION_SOCKET,
        rx_socket_name=NAVEL_MOTION_SOCKET,
    ):
        super().__init__(socket_name, rx_socket_name)


class Speech(_messages.SpeechMessenger):
    """Send and receive messages via speech socket

    This class is able to transceive protobuf messages via a unix
    domain socket (UDS). As soon as the object is created it will
    attempt to connect to the socket. If socket connection is successful,
    methods can be used to send messages. Each message is converted
    into a protobuf format before being sent to the speech socket.

    It also provides a mechanism for registerig bookmarks in the text.
    This is run asynchronously as messages could arrive at any point in
    time. Read messages are accessed using callback functions.
    If there are no relevent callback functions then messages will be thrown
    away to keep buffer clear. See valid keys to see what callbacks are
    supported.

    If the object where data is stored by callback functions is to be accessed
    by any other threads, steps must be taken to make it threadsafe.

    Args:
        socket_name (str, optional): Name of the socket to connect to.
            Defaults to NAVEL_SPEECH_SOCKET
    """

    def __init__(self, socket_name=NAVEL_SPEECH_SOCKET):
        super().__init__(socket_name)


class Perception(_messages.PerceptionMessenger):
    """Send and receive messages from perception socket

    This class is able to transceive protobuf messages via a unix
    domain socket (UDS). As soon as the object is created it will
    attempt to connect to the socket. If socket connection is successful,
    methods can be used to send and receive messages. Each message is converted
    from a protobuf format and into a navel data struct.

    Args:
        socket_name (str, optional): Name of the socket to connect to.
            Defaults to NAVEL_PERCEPTION_SOCKET
    """

    def __init__(self, socket_name=NAVEL_PERCEPTION_SOCKET):
        super().__init__(socket_name)


class Robot(Motion, Perception, Speech):
    """Send commands and receive data from robot.

    This class can be used to send motion or speech commands, register
    callbacks for bookmarks, fetch the latest perception data, and set
    robot configuration values. It should always be used as a context
    manager (inside a ``with`` block).
    """

    def __init__(self):
        Motion.__init__(self, None, None)
        Perception.__init__(self, None)
        Speech.__init__(self, None)
        self._sockets = {}
        self._mixer = None

    def open(self):
        AsyncRunner.open(self)

    def close(self):
        for socket in self._sockets.values():
            socket.disconnect()

        self._sockets = {}
        AsyncRunner.close(self)

    @property
    def _motion_sock(self):
        return self._get_or_init_prop(NAVEL_MOTION_SOCKET)

    @property
    def _motion_rx_sock(self):
        return self._get_or_init_prop(NAVEL_MOTION_RX_SOCKET)

    @property
    def _perc_sock(self):
        return self._get_or_init_prop(NAVEL_PERCEPTION_SOCKET)

    @property
    def _speech_sock(self):
        return self._get_or_init_prop(NAVEL_SPEECH_SOCKET)

    def _get_or_init_prop(self, name):
        if not self._active:
            raise RuntimeError(
                'Robot communication should only be done inside "with" block'
            )
        if name not in self._sockets:
            self._sockets[name] = _messages.ProtobufSocket(name)
        return self._sockets[name]

    @property
    def mixer(self) -> alsaaudio.Mixer:
        if self._mixer is None:
            self._mixer = alsaaudio.Mixer(control="MVC1", cardindex=0)

        return self._mixer

    @property
    def volume(self) -> int:
        """Get/set current volume of the robot speakers, range [0, 100]."""

        vol_max = MVC1_VOL_LIMIT * MVC1_VOL_MAX
        vol = self.mixer.getvolume(units=alsaaudio.VOLUME_UNITS_RAW)[0]
        vol = round((vol / vol_max) ** (1 / 0.15) * 100)

        return vol

    @volume.setter
    def volume(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise ValueError("Only volumes between 0 and 100 are supported")

        vol_max = MVC1_VOL_LIMIT * MVC1_VOL_MAX
        vol = round((value / 100) ** 0.15 * vol_max)

        self.mixer.setvolume(vol, units=alsaaudio.VOLUME_UNITS_RAW)

    def __repr__(self):
        return "Robot()"

    def __str__(self):
        return self.__repr__()


def run(app):
    """Run a coroutine with a robot connection as the only parameter.

    This is used to start navel "apps". This function is only provided
    as a shorthand for the most common use-case, calling the run
    method on any of the connection classes accomplishes the same goal.
    """
    warn(
        "Function .run() is deprecated and will be removed in a future version. Please check the getting started guide for the recommended way to start coroutines.",
        DeprecationWarning,
        stacklevel=2,
    )

    async def wrapped():
        async with Robot() as r:
            return await app(r)

    return asyncio.run(wrapped())
