from __future__ import annotations

import asyncio
import math
import time
from typing import Awaitable, Callable, List

import bitstring
import navel._data_structs as ds
from navel._async import AsyncRunner, runner_task
from navel._pyproto import cns_pb2 as _cns
from navel._pyproto import klframe_pb2 as _klframe
from navel._pyproto import payload_pb2 as _payload
from navel._pyproto import perc_pb2 as _perc
from navel._pyproto import speech_pb2 as _speech
from navel._socket_coms import ProtobufSocket

# Wait between read socket calls in seconds
RECV_SLEEP = 0.04

# Constants for tts activity detection
TTS_STATE_NOT_SPEAKING = "PREPARED"
TTS_PROC_FILE = "/proc/asound/APE/pcm2p/sub0/status"

# Size of bodyd text buffer
SPEECH_BUF_SIZE = 1024
SPEECH_BUF_SLOTS = 128


class MotionMessenger(AsyncRunner):
    def __init__(
        self, socket_name: str | None = None, rx_socket_name: str | None = None
    ):
        self._socket_name = socket_name
        self._rx_socket_name = rx_socket_name
        self._arms = None
        self._tilts = None
        super().__init__()

    def open(self):
        self._motion_sock = ProtobufSocket(self._socket_name)
        self._motion_rx_sock = ProtobufSocket(self._rx_socket_name)
        super().open()

    def close(self):
        self._motion_sock.disconnect()
        self._motion_rx_sock.disconnect()
        super().close()

    @runner_task
    async def next_odometry(
        self, timeout: float = 1
    ) -> Awaitable[ds.OdometryData]:
        """Receives next packet of odometry data from the robot.

        Will always return the newest available packet, which may be from
        slightly before the function was called, but never a duplicate.
        In general, packets should arrive roughly every 0.1s.

        Args:
            timeout (float, optional): Maximum time to wait for a packet
                in seconds. Defaults to 1.

        Raises:
            ConnectionAbortedError: If socket connection is lost
            TimeoutError: If timeout is triggered.

        Returns:
            Awaitable[OdometryData]: The received data.
        """

        start = time.time()
        match = None

        while time.time() - start < timeout:
            try:
                msg = self._motion_rx_sock.recv()
            except BlockingIOError:
                if match is not None:
                    return _parse_odometry_msg(match)
                await asyncio.sleep(RECV_SLEEP)
                continue

            if msg is None:  # Occurs if socket connection lost
                raise ConnectionAbortedError("Socket connection lost")

            if msg.ptype == _klframe.CNS_ODOM:
                match = msg

        raise TimeoutError()

    @runner_task
    async def look_at_cart(self, cart: ds.CartSys3d, head: float):
        """Sends a message for robot to look at a point in space.

        Args:
            cart (CartSys3d): 3d target point to look at.
            head (float): Magnitude of head movement towards point, as compared
                to eye movement, where 0 is no head movement and 1 is maximum
                head movement.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.LookatCart()
        msg.cart.sys = cart.sys
        msg.cart.x = cart.x * 1000
        msg.cart.y = cart.y * 1000
        msg.cart.z = cart.z * 1000
        msg.head = head

        self._motion_sock.send(msg, _klframe.LOOKAT_CART)
        await asyncio.sleep(0.5)

    @runner_task
    async def look_at_px(self, px: ds.Point2d, head: float):
        """Sends a message to robot to look at a pixel.

        Args:
            px (Point2d): 2d point on the image plane.
            head (float): Magnitude of head movement towards point, as compared
                to eye movement, where 0 is no head movement and 1 is maximum
                head movement.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.LookatPx()
        msg.px.x = px.x
        msg.px.y = px.y
        msg.head = head

        self._motion_sock.send(msg, _klframe.LOOKAT_PX)
        await asyncio.sleep(0.5)

    @runner_task
    async def look_at_person(self, uid: int, head: float):
        """Sends a message setting which person robot should look at.

        Args:
            uid (int): Unique identifier of person.
            head (float): Magnitude of head movement towards point, as compared
                to eye movement, where 0 is no head movement and 1 is maximum
                head movement.
        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.LookatPerson()
        msg.uid = uid
        msg.head = head

        self._motion_sock.send(msg, _klframe.LOOKAT_PERSON)
        await asyncio.sleep(0.5)

    @runner_task
    async def head_overlay(self, overlay: ds.Bryan):
        """Sends a message rotating the head from its natural position (which
            is determined by the direction of focus) using Tait-Bryan angles.

        Args:
            overlay (Bryan): Tait-Bryan angles describing offset from natural
                position.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.HeadOverlay()
        msg.overlay.x = overlay.x
        msg.overlay.y = overlay.y
        msg.overlay.z = overlay.z

        self._motion_sock.send(msg, _klframe.HEAD_OVERLAY)

    @runner_task
    async def head_path_limits(self, v_max: float, a_max: float, j_max: float):
        """Sends pathplanner limits for head motion to robot.

        Args:
            v_max (float): Maximum velocity.
            a_max (float): Maximum acceleration.
            j_max (float): Maximum jerk.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.HeadBndry()
        msg.v_max = v_max
        msg.a_max = a_max
        msg.j_max = j_max
        self._motion_sock.send(msg, _klframe.HEAD_BNDRY)

    @runner_task
    async def head_facial_expression(
        self,
        neutral: float = 0,
        happy: float = 0,
        sad: float = 0,
        surprise: float = 0,
        anger: float = 0,
        smile: float = 0,
    ):
        """Sends a message setting the facial expression of the robot.

        This function sets the magnitude of each of the robots five expressions.
        Each argument contains a scalar value of how extreme the argument
        emotion is, where emotion max is 1 and emotion minimum is 0.

        Args:
            neutral (float): Sets magnitude of neutral expression.
            happy (float): Sets magnitude of happy expression.
            sad (float): Sets magnitude of sad expression.
            surprise (float): Sets magnitude of surprise expression.
            anger (float): Sets magnitude of anger expression.
            smile (float): Sets magnitude of smile expression.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.HeadFe()
        msg.neutral = neutral
        msg.happy = happy
        msg.sad = sad
        msg.surprise = surprise
        msg.anger = anger
        msg.smile = smile

        self._motion_sock.send(msg, _klframe.HEAD_FE)

    @runner_task
    async def head_eyelids(self, openness_l: float, openness_r: float):
        """Sends a message setting how open the eyes should be.

        Args:
            openness_l (float): Scalar value of how open left eye should be,
                where 1 is open and 0 is closed.
            openness_r (float): Scalar value of how open right eye should be,
                where 1 is open and 0 is closed.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.HeadEyelids()
        msg.openness_l = openness_l
        msg.openness_r = openness_r

        self._motion_sock.send(msg, _klframe.HEAD_EYELIDS)

    @runner_task
    async def head_mouth(self, openness: float):
        """Sends a message setting how wide the mouth should be open.

        Args:
            openness (float): Scalar value which controls how wide mouth
                should be open, 1 = open, 0 = closed.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.HeadMouth()
        msg.openness = openness

        self._motion_sock.send(msg, _klframe.HEAD_MOUTH)

    @runner_task
    async def config_set(self, name, value, valType):
        """Sends a message to change the value of a config field.

        Args:
            name (str): Name of config field to set. Parameters can be explored
                in browser interface. Concatenate name segments from
                there, e.g. "rndr_rgbsensor_max_brightness".
            value (int or float): Value to set.
            valType (DataType): DataType Enum describing value datatype.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.ConfigSet()
        msg.name = name

        if valType == ds.DataType.I32:
            msg.i32 = value
        elif valType == ds.DataType.U32:
            msg.u32 = value
        elif valType == ds.DataType.I64:
            msg.i64 = value
        elif valType == ds.DataType.U64:
            msg.u64 = value
        elif valType == ds.DataType.F32:
            msg.f32 = value
        elif valType == ds.DataType.F64:
            msg.f64 = value

        else:
            raise ValueError("Unknown data type")

        self._motion_sock.send(msg, _klframe.CONFIG_SET)

    @runner_task
    async def move_base(
        self,
        distance: float,
        speed: float | None = None,
        acceleration: float | None = None,
    ):
        """Sends a move command to robot.

        Command translates the robot forward/backward by desired distance.
        If no speed/acceleration are defined, the maximum will be used.

        Args:
            distance (float): Motion magnitude and direction in meters.
            speed (float): Desired peak speed (m/s).
            acceleration (float): Desired peak acceleration (m/s²).

        Raises:
            ValueError: When speed/acceleration are outside limits.
            SocketError: When message cannot be sent via socket.
        """

        # TODO: get this from bodyd
        peak_speed = 1.6
        peak_acc = 1.2

        if speed is None:
            speed = peak_speed
        if acceleration is None:
            acceleration = peak_acc

        _check_limits(speed, 0, peak_speed, "Speed")
        _check_limits(acceleration, 0, peak_acc, "Acceleration")

        t_c, t_a = _calc_motion_times(distance, speed, acceleration)
        v = int(math.copysign(speed, distance) * 10000)  # µm / 10 ms

        await self._move(t_c, t_a, v, 0)

    @runner_task
    async def rotate_base(
        self,
        angle: float,
        speed: float | None = None,
        acceleration: float | None = None,
    ):
        """Sends a rotate command to robot.

        Command rotates the robot around Z axis by desired angle.
        If no speed/acceleration are defined, the maximum will be used.

        Args:
            angle (float): Rotation magnitude and direction in degrees.
            speed (float): Desired peak speed (deg/s).
            acceleration (float): Desired peak acceleration (deg/s²).

        Raises:
            ValueError: When speed/acceleration are outside limits.
            SocketError: When message cannot be sent via socket.
        """

        # TODO: get this from bodyd
        peak_speed = 70
        peak_acc = 60

        if speed is None:
            speed = peak_speed
        if acceleration is None:
            acceleration = peak_acc

        _check_limits(speed, 0, peak_speed, "Speed")
        _check_limits(acceleration, 0, peak_acc, "Acceleration")

        t_c, t_a = _calc_motion_times(angle, speed, acceleration)
        # µrad / 10 ms
        v = int(math.copysign(speed, angle) * 10000 / 180 * math.pi)

        await self._move(t_c, t_a, 0, v)

    @runner_task
    async def move_and_rotate_base(
        self,
        distance: float,
        angle: float,
        speed: float | None = None,
        acceleration: float | None = None,
    ):
        """Sends both a move and a rotate command to robot.

        Command translates the robot forward/backward by the desired
        distance and rotates it around Z axis by desired angle.
        If no speed/acceleration are defined, the maximum will be used.
        Rotational speed is calculated to match movement speed.

        Warning: rotation amount is likely to be inaccurate, some trial
        and error may be necessary to define wanted movements.

        Args:
            distance (float): Motion magnitude and direction in meters.
            angle (float): Rotation magnitude and direction in degrees.
            speed (float): Desired peak movement speed (m/s).
            acceleration (float): Desired peak acceleration (m/s²).

        Raises:
            ValueError: When speed/acceleration are outside limits.
            SocketError: When message cannot be sent via socket.
        """

        # TODO: get this from bodyd
        peak_speed = 0.25
        peak_acc = 1
        if speed is None:
            speed = peak_speed
        if acceleration is None:
            acceleration = peak_acc
        _check_limits(speed, 0, peak_speed, "Speed")
        _check_limits(acceleration, 0, peak_acc, "Acceleration")

        t_c, t_a = _calc_motion_times(distance, speed, acceleration)
        vl = int(math.copysign(speed, distance) * 10000)

        acc_time = t_a / 100
        const_time = t_c / 100
        spd = angle / (const_time + acc_time)  # should be the peak speed
        vr = int(math.copysign(spd, angle) * 10000 / 180 * math.pi)

        await self._move(t_c, t_a, vl, vr)

    def base_vel(self, x: float, r: float):
        """Sends a single move command to robot.

        Command sets the robot speed to desired value, if after 10ms no new
        base_vel has been sent, then robot will start to decrease velocity.
        To keep robot at same velocity, issue this command with the desired
        speed every 10ms.

        The acceleration will be limited by the hardware.

        Args:
            x (float): Linear motion velocity in meter per second.
            r (float): Anticlockwise rotation (around Z) velocity in radians
                per second.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        self._base_move(int(x * 10000), int(r * 10000))

    async def _move(self, t_c, t_a, v_l, v_r):
        for i in range(t_a):
            lin = int(_ramp(i, t_a) * v_l)
            rot = int(_ramp(i, t_a) * v_r)

            self._base_move(lin, rot)
            await asyncio.sleep(0.0099)

        for i in range(t_c):  # constant vel
            self._base_move(v_l, v_r)
            await asyncio.sleep(0.0099)

        for i in reversed(range(t_a)):
            lin = int(_ramp(i, t_a) * v_l)
            rot = int(_ramp(i, t_a) * v_r)

            self._base_move(lin, rot)
            await asyncio.sleep(0.0099)

    @runner_task
    async def approach_person(self, uid: int):
        """Sends a message setting which person robot should approach.

        Args:
            uid (int): Unique identifier of person.
        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        msg = _payload.ApproachPerson()
        msg.uid = uid

        self._motion_sock.send(msg, _klframe.APPROACH_PERSON)
        await asyncio.sleep(0.5)

    def approach_person_cancel(self):
        """Sends a cancel approach command to robot."""

        msg = _payload.ApproachPersonCancel()

        self._motion_sock.send(msg, _klframe.APPROACH_PERSON_CANCEL)

    @runner_task
    async def rotate_arms(self, left_angle: float, right_angle: float):
        """Sends rotate arms command to robot.

        The arm motion is limited in the upper back and arms can not do a full
        rotation. Rotation is around robot's -Y axis, 0 is straight down,
        positive is generally up and negative is generally down.

        Args:
            angle_l (float): Absolute rotation of left arm in degrees.
            angle_r (float): Absolute rotation of right arm, in degrees.

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        # TODO: move to bodyd
        factor = 3100000 / 180

        msg = _payload.Arms()
        msg.angle_l = int(left_angle * factor)
        msg.angle_r = int(-right_angle * factor)

        self._motion_sock.send(msg, _klframe.ARMS)

        curr = (left_angle, right_angle)
        d = 245 if self._arms is None else _max_diff(curr, self._arms)
        self._arms = curr
        await asyncio.sleep(0.5 + d / 180 * 2)

    @runner_task
    async def tilt_base(self, x_percent: float, y_percent: float):
        """Sends tilt body command to robot.

        Args:
            x (float): Tilt around X axis as a fraction of maximum.
                -1 (left) to 1 (right).
            y (float): Tilt around Y axis as a fraction of maximum.
                -1 (backwards) to 1 (forwards).

        Raises:
            SocketError: In cases where message cannot be sent via socket.
        """

        center_x = 0
        amp_x = 1000
        center_y = 0
        amp_y = 1000

        msg = _payload.Basetilt()
        msg.x = int(x_percent * amp_x + center_x)
        msg.y = int(y_percent * amp_y + center_y)

        self._motion_sock.send(msg, _klframe.BASETILT)

        curr = (x_percent, y_percent)
        d = 2 if self._tilts is None else _max_diff(curr, self._tilts)
        self._tilts = curr
        await asyncio.sleep(0.5 + d / 2)

    def _base_move(self, x, r):
        msg = _payload.Baseinc()
        msg.x = x
        msg.y = 0
        msg.z = r

        self._motion_sock.send(msg, _klframe.BASEINC)


def _check_limits(val, minimum, maximum, name):
    if val > maximum:
        raise ValueError(f"{name} above allowed maximum ({maximum}).")
    if val < minimum:
        raise ValueError(f"{name} below allowed minimum ({minimum}).")


def _calc_motion_times(dist, speed, acceleration):
    if speed == 0 or acceleration == 0 or dist == 0:
        return 0, 0

    acc_time = speed / acceleration

    # Make sure we don't go too far while accelerating to target speed

    while True:
        c_dist = abs(dist) - acc_time * speed  # symmetric acc/dec
        if c_dist >= 0:
            break
        acc_time -= 0.01  # minimum time step

    t_c = int(c_dist / speed * 100)  # constant travel time in 10ms
    t_a = int(acc_time * 100)  # acc/brake time in 10ms

    return t_c, t_a


def _ramp(i, m):
    """sine ramp: 0 to m -> 0 to 0.5"""
    return (-math.cos(math.pi * i / m) + 1) / 2


def _max_diff(curr, prev):
    return max((abs(curr[0] - prev[0]), abs(curr[1] - prev[1])))


class SpeechMessenger(AsyncRunner):
    """Class containing methods to access speech messages.

    This class contains methods to send and receive speech messages. As robot
    also returns messages on this socket this class inherits AsyncSocketListener
    to asynchronously detect such messages. Incoming messages are read by
    internal message handler.
    """

    def __init__(self, socket_name: str | None = None):
        self._socket_name = socket_name
        self._bookmark_cbs = {}
        super().__init__()

    def open(self):
        self._speech_sock = ProtobufSocket(self._socket_name)
        super().open()

    def close(self):
        self._speech_sock.disconnect()
        super().close()

    async def _handle_bookmark(self, num):
        if num in self._bookmark_cbs:
            asyncio.create_task(self._bookmark_cbs[num](self))

    @runner_task
    async def say(self, text: str):
        """Sends a speech text message to speech socket.
        If the message is too long, it may be split up
        and sent as parts.

        Args:
            text (str): contents of message to be sent to speech socket.

        Raises:
            TypeError: If text is not string
            SocketError: If errors connecting to socket or sending message
        """

        parts = _split_text_recursive([text])
        try:
            await self._say_all(parts)
        except asyncio.CancelledError:
            self._cancel_speech()
            raise

    async def _say_all(self, parts: list[str]):

        for i in range(len(parts) // SPEECH_BUF_SLOTS + 1):
            for part in parts[
                SPEECH_BUF_SLOTS * i : SPEECH_BUF_SLOTS * (i + 1)
            ]:
                self._say_one(part)

            # Small wait to let everything start properly
            # Otherwise we get glitches in is_speaking()
            await asyncio.sleep(RECV_SLEEP)

            # Wait until we start speaking
            while not is_speaking():
                await asyncio.sleep(RECV_SLEEP)

            # Wait until we're done speaking
            while is_speaking():
                try:
                    msg = self._speech_sock.recv()
                except BlockingIOError:
                    await asyncio.sleep(RECV_SLEEP)
                    continue

                if msg.ptype == _klframe.SPEECH_BOOKMARK:
                    await self._handle_bookmark(_parse_bookmark_msg(msg))

    def _say_one(self, text: str):

        msg = _speech.SpeechText()
        msg.speech = text

        self._speech_sock.send(msg, _klframe.SPEECH_TEXT)

    def _cancel_speech(self):

        msg = _speech.SpeechCancel()

        self._speech_sock.send(msg, _klframe.SPEECH_CANCEL)

    def set_bookmark_callback(
        self, bookmark: int, action: Callable[[SpeechMessenger], Awaitable]
    ) -> None:
        """Sets a callback for the given bookmark number.

        Args:
            bookmark (int): Bookmark number to bind this action to.

            action (callable): Function that should be called.
                Must be async and take a reference to this object
                as its only parameter
        """

        self._bookmark_cbs[bookmark] = action


def _split_text_recursive(
    parts: list[str], delimiters: list[str] = ("\n\n", "\n", ".", ",", " ")
) -> list[str]:
    ret = []
    for part in parts:
        if part and len(part) < SPEECH_BUF_SIZE:
            ret.append(part)
            continue

        split_part = [p + delimiters[0] for p in part.split(delimiters[0])]

        if len(delimiters) > 1:
            split_part = _split_text_recursive(split_part, delimiters[1:])
        else:
            # If no delimiters left, just split into sections of the right size
            _ls = []
            for p in split_part:
                _ls.extend(
                    [
                        p[SPEECH_BUF_SIZE * i : SPEECH_BUF_SIZE * (i + 1)]
                        for i in range(len(p) // SPEECH_BUF_SIZE)
                    ]
                )

            split_part = _ls

        ret.extend(split_part)

    ret = _combine_text(ret)
    return ret


def _combine_text(parts):
    combined = []
    current = ""
    for idx, p in enumerate(parts):
        nxt = current + p
        if len(nxt) >= SPEECH_BUF_SIZE:
            combined.append(current)
            current = p
            if idx == len(parts) - 1:
                combined.append(p)
        elif idx == len(parts) - 1:
            combined.append(nxt)
        else:
            current = nxt

    return combined


def is_speaking():
    # Extract current state from first line in proc file
    with open(TTS_PROC_FILE, "r") as fp:
        for line in fp:
            if "state:" in line:
                state = line.split()[1]

                # Differnt states can mean speaking, only one means silence
                return state != TTS_STATE_NOT_SPEAKING

    return False


class PerceptionMessenger(AsyncRunner):
    """Class for accessing perception messages."""

    def __init__(self, socket_name: str | None = None):
        self._socket_name = socket_name
        super().__init__()

    def open(self):
        self._perc_sock = ProtobufSocket(self._socket_name)
        super().open()

    def close(self):
        self._perc_sock.disconnect()
        super().close()

    @runner_task
    async def next_frame(
        self, timeout: float = 1
    ) -> Awaitable[ds.PerceptionData]:
        """Receives next frame of perception data from the robot.

        Will always return the newest available frame, which may be from
        slightly before the function was called, but never a duplicate.
        In general, frames should arrive roughly every 0.1s.

        Args:
            timeout (float, optional): Maximum time to wait for a frame
                in seconds. Defaults to 1.

        Raises:
            ConnectionAbortedError: If socket connection is lost
            TimeoutError: If timeout is triggered.

        Returns:
            Awaitable[PerceptionData]: The received perception data.
        """

        start = time.time()
        match = None

        while time.time() - start < timeout:
            try:
                msg = self._perc_sock.recv()
            except BlockingIOError:
                if match is not None:
                    return _parse_perception_msg(match)
                await asyncio.sleep(RECV_SLEEP)
                continue

            if msg is None:  # Occurs if socket connection lost
                raise ConnectionAbortedError("Socket connection lost")

            if msg.ptype == _klframe.PERC:
                match = msg

        raise TimeoutError()

    @runner_task
    async def set_persist(self, uid: int):
        """Sends a message to robot to add person to persistent storage.

        Args:
            uid (int): Unique identifier of person.
        Raises:
            ValueError: When uid is outside limits.
            SocketError: In cases where message cannot be sent via socket.
        """

        uid_min = 1
        uid_max = 2147483647  # RAND_MAX

        _check_limits(uid, uid_min, uid_max, "UID")

        msg = _payload.UidRemember()
        msg.uid = uid

        self._perc_sock.send(msg, _klframe.UID_REMEMBER)
        await asyncio.sleep(0.5)

    @runner_task
    async def clear_persist(self, uid: int):
        """Sends a message to robot to remove person from persistent storage.

        Args:
            uid (int): Unique identifier of person.
        Raises:
            ValueError: When uid is outside limits.
            SocketError: In cases where message cannot be sent via socket.
        """

        uid_min = 1
        uid_max = 2147483647  # RAND_MAX

        _check_limits(uid, uid_min, uid_max, "UID")

        msg = _payload.UidForget()
        msg.uid = uid

        self._perc_sock.send(msg, _klframe.UID_FORGET)
        await asyncio.sleep(0.5)

    @runner_task
    async def get_id_store(self, timeout: float = 1) -> List[ds.PerceptionId]:
        """Sends a message to the robot to receive the id store.

        Args:
            timeout (float, optional): Timeout for received data in seconds.
                Defaults to 1.

        Raises:
            ConnectionAbortedError: If socket connection is lost.
            TimeoutError: If timeout is triggered.

        Returns:
            List[ds.PerceptionId]: A list of perception ids currently held.
        """

        msg = _perc.UidGetDesc()

        self._perc_sock.send(msg, _klframe.UID_GET_DESC)
        await asyncio.sleep(0.5)

        start = time.time()
        match = None

        while time.time() - start < timeout:
            try:
                msg = self._perc_sock.recv()
            except BlockingIOError:
                if match is not None:
                    return _parse_perception_id_msg(match)
                await asyncio.sleep(RECV_SLEEP)
                continue

            if msg is None:  # Occurs if socket connection lost
                raise ConnectionAbortedError("Socket connection lost")

            if msg.ptype == _klframe.UID_GET_DESC:
                match = msg

        raise TimeoutError()


def _parse_asr_duration(msg):
    asr_state = _speech.SpeechAsrState()
    asr_state.ParseFromString(msg.data)

    return asr_state.speaker_duration


def _parse_bookmark_msg(msg):
    bookmark = _speech.SpeechBookmark()
    bookmark.ParseFromString(msg.data)

    return bookmark.bookmark


# Following functions covert from protobuf to api versions of data classes.
# This is done for two reasons, firstly to improve documentation and names,
# and secondly to hide some protobuf methods and fields from external users.


def _parse_perception_id_msg(msg) -> List[ds.PerceptionId]:
    data = _perc.UidGetDesc()
    data.ParseFromString(msg.data)

    return [_convert_perc_id(entry) for entry in data.perc_ids]


def _parse_perception_msg(msg) -> ds.PerceptionData:
    data = _perc.PercData()
    data.ParseFromString(msg.data)

    flags = bitstring.BitArray(uint=data.flags, length=32)
    flags.reverse()

    # Flags is proven to now be in proper order, PERC_FLAG_FACES leftmost,
    # accessible with flags.all(True, [0]) as expected
    # length should be same as perc.h struct perc_data.flags bit length

    output = ds.PerceptionData()

    output.time = data.time

    for person in data.pers:
        per_out = ds.Person()

        per_out.uid = person.uid

        # Check what fields are valid
        if flags.any(True, [0]):  # PERC_FLAG_FACES
            per_out.face = _convert_bbox_2ds(person.face)
            per_out.dist_mm = person.dist_mm

        if flags.any(True, [1]):  # PERC_FLAG_LM
            per_out.landmarks = _convert_landmarks(person.lm)

        if flags.any(True, [2]):  # PERC_FLAG_HP
            per_out.head_position = _convert_bryan(person.hp)

        if flags.any(True, [3]):  # PERC_FLAG_FER
            per_out.facial_expression = _convert_fer(person.fer)

        if flags.any(True, [4]):  # PERC_FLAG_FACEID
            per_out.id_score = person.id_score

        if flags.any(True, [5]):  # PERC_FLAG_GAZE
            per_out.gaze = _convert_cart_vec_3d(person.gaze)
            per_out.gaze_overlap = person.gaze_overlap

        if flags.any(True, [6]):  # PERC_FLAG_REF_HP
            _convert_ref_hp(person, per_out)

        output.persons.append(per_out)

    output.sst_time_latest = data.sst_time_latest

    for track_in in data.sst_track_latest:
        track = ds.SstMeta(
            track_in.id,
            track_in.activity,
            _convert_cart_sys_3d(track_in.loc),
            track_in.is_dynamic,
        )
        output.sst_tracks_latest.append(track)

    return output


def _parse_odometry_msg(msg):
    data = _cns.OdometryData()
    data.ParseFromString(msg.data)

    # Set position (x, y, z)
    position = ds.Position(
        data.base_position[0] / 1000000.0,
        data.base_position[1] / 1000000.0,
    )
    # Set orientation (quaternion)
    orientation = ds.Orientation(
        math.sin(data.base_position[2] / 1000000 / 2.0),
        math.cos(data.base_position[2] / 1000000 / 2.0),
    )

    # Set linear and angular velocity
    velocity = ds.Velocity(
        data.base_velocity[0] / 1000.0,
        data.base_velocity[1] / 1000.0,
    )

    odom = ds.OdometryData(
        data.time,
        position,
        orientation,
        velocity,
    )

    return odom


def _convert_perc_id(input) -> ds.PerceptionId:
    flags = bitstring.BitArray(uint=input.flags, length=32)
    flags.reverse()

    is_persistent = flags.any(True, [0])  # PERC_ID_FLAG_PERSISTENT

    return ds.PerceptionId(input.uid, is_persistent=is_persistent)


def _convert_ref_hp(input, output):
    output.g_eye_left = _convert_coord_system_list(input.g_eye_l)
    output.g_eye_right = _convert_coord_system_list(input.g_eye_r)
    output.g_nose = _convert_coord_system_list(input.g_nose)
    output.g_head_position = _convert_coord_system_list(input.g_hp)
    output.g_gaze = _convert_coord_system_list(input.g_gaze)

    return output


def _convert_coord_system_list(input):
    if input is None:
        return None

    if input[0].sys == 0:
        return None

    output = []

    for i in range(len(input)):
        output.append(_convert_cart_sys_3d(input[i]))

    return output


def _convert_coord_system(input):
    output = ds.CoordSystem(input)

    return output


def _convert_cart_vec_3d(input):
    output = ds.CartVec3d(
        input.x,
        input.y,
        input.z,
    )

    return output


def _convert_bbox_2ds(input):
    output = ds.Bbox2d(
        input.x1,
        input.y1,
        input.x2,
        input.y2,
    )

    return output


def _convert_point_2D(input):
    output = ds.Point2d(
        input.x,
        input.y,
    )

    return output


def _convert_bryan(input):
    output = ds.Bryan(
        input.x,
        input.y,
        input.z,
    )

    return output


def _convert_cart_sys_3d(input):
    output = ds.CartSys3d(
        _convert_coord_system(input.sys),
        input.x / 1000,
        input.y / 1000,
        input.z / 1000,
    )

    return output


def _convert_landmarks(input):
    output = ds.PersonLandmarks(
        _convert_point_2D(input.eye_l),
        _convert_point_2D(input.eye_r),
        _convert_point_2D(input.nose),
        _convert_point_2D(input.mouth_l),
        _convert_point_2D(input.mouth_r),
    )

    return output


def _convert_fer(input):
    output = ds.PersonFacialExpression(
        input.neutral,
        input.happy,
        input.sad,
        input.surprise,
        input.anger,
    )

    return output
