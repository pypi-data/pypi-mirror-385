from dataclasses import dataclass, field
from enum import IntEnum
from typing import List


class DataType(IntEnum):
    """Enum class describing what data type is used."""

    I32 = 1  #: 32 bit integer
    U32 = 2  #: 32 bit unsigned integer
    I64 = 3  #: 64 bit integer
    U64 = 4  #: 64 bit unsigned integer
    F32 = 5  #: 32 bit float
    F64 = 6  #: 64 bit double


class CoordSystem(IntEnum):
    """Enum class describing available coordinate frames. X generally points
    forward, Y to the left and Z upwards (from point of view of robot).
    """

    CAM_CHEST = 1  #: Origin in center of chest cam, not implemented yet
    HEAD_REF = 2  #: Origin in head center, head facing slightly downwards.
    HEAD_STRAIGHT = 3  #: Origin in head center, head facing straight.
    HEAD_REAL = 4  #: Fixed to head, x axis pointing in facing direction.
    CAM_HEAD = 5  #: Origin in center of head cam.
    EYE_LEFT = 6  #: Origin in center of left eye.
    EYE_RIGHT = 7  #: Origin in center of right eye.
    COORD_LEN = 8  #: Max Value of enum, used only in calculations


@dataclass
class CartVec3d(object):
    """Describes a cartesian 3D vector.

    Args:
            x (float): X vector.
            y (float): Y vector.
            z (float): Z vector.
    """

    x: float
    y: float
    z: float


@dataclass
class Bbox2d(object):
    """Describes a bounding box with two 2D points.

    Sets the limits of a bounding Box located in an image. The bounding
    box limits are described in pixels in XY plane.

    Args:
        x1 (int): Point 1 X coordinate in pixels.
        y1 (int): Point 1 Y coordinate in pixels.
        x2 (int): Point 2 X coordinate in pixels.
        y2 (int): Point 2 Y coordinate in pixels.
    """

    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class Point2d(object):
    """Describes a 2D point using pixel coordinates.

    Args:
        x (int): X coordinate in pixels.
        y (int): Y coordinate in pixels.
    """

    x: int
    y: int


@dataclass
class Bryan(object):
    """Describes a Tait-Bryan angle rotation.

    Args:
        x (float): Rotation around X axis in radians.
        y (float): Rotation around Y axis in radians.
        z (float): Rotation around Z axis in radians.
    """

    x: float
    y: float
    z: float


@dataclass
class CartSys3d(object):
    """Describes a 3D point in cartesian space.

    Args:
        sys (CoordSystem): Coordinate system used.
        x (float): X coordinate in meters.
        y (float): Y coordinate in meters.
        z (float): Z coordinate in meters.
    """

    sys: CoordSystem
    x: float
    y: float
    z: float


@dataclass
class PersonFacialExpression(object):
    """Class describing the facial expression of the detected person

    Each emotion in this class is described by a magnitude where 1
    describes maximum expression and 0 describes minimum expression.

    Args:
        neutral (float): magnitude of neutral.
        happy (float): magnitude of happyness.
        sad (float): magnitude of sadness.
        surprise (float): magnitude of surprise.
        anger (float): magnitude of anger.
    """

    neutral: float
    happy: float
    sad: float
    surprise: float
    anger: float


@dataclass
class PersonLandmarks(object):
    """Class describing position of a person's facial landmarks.

    Each landmark is described by its 2D position within the host image.

    Args:
        eye_left (Point2d): Position of left eye.
        eye_right (Point2d): Position of right eye.
        nose (Point2d): Position of nose.
        mouth_left (Point2d): Position of left end of mouth.
        mouth_right (Point2d): Position of right end of mouth.
    """

    eye_left: Point2d
    eye_right: Point2d
    nose: Point2d
    mouth_left: Point2d
    mouth_right: Point2d


@dataclass
class Person(object):
    """Defines attributes of a detected person.

    Args:
        id_score (float):
            Defaults to None.
        uid (int): Unique user id.
            Defaults to None.
        face (Bbox2d): Bounding box of face.
            Defaults to None.
        landmarks (PersonLandmarks): Position of left end of mouth.
            Defaults to None.
        head_position (Bryan): Position of head in Tait-Bryan angles (radians).
            Defaults to None.
        gaze (CartVec3d): Vector describing persons direction of gaze.
            Defaults to None.
        facial_expression (PersonFacialExpression): Person's facial expression.
            Defaults to None.
        dist_mm (float): Distance from robot to person (mm).
            Defaults to None.
        gaze_overlap (float): How much person is staring at robot, 0 = not
            looking at robot, 1 = looking directly at robot.
            Defaults to None.
        g_eye_left (list[CartSys3d]): A list of the position of left eye in all coord
            frames. This might be out of frame, then sys is CoordSystem.UNDEFINED.
            Defaults to None.
        g_eye_right (list[CartSys3d]): A list of the position of right eye in all
            coord frames. This might be out of frame, then sys is
            CoordSystem.UNDEFINED.
            Defaults to None.
        g_nose (list[CartSys3d]): A list of the position of nose in all
            coord frames. This might be out of frame, then sys is
            CoordSystem.UNDEFINED.
            Defaults to None.
        g_head_position (list[CartSys3d]): A list of the position of head in all
            coord frames.
            Defaults to None.
        g_gaze (list[CartSys3d]): A list of the target of persons gaze in all
            coord frames.
            Defaults to None.
    """

    id_score: float | None = None
    uid: int | None = None
    face: Bbox2d | None = None
    landmarks: PersonLandmarks | None = None
    head_position: Bryan | None = None
    gaze: CartVec3d | None = None
    facial_expression: PersonFacialExpression | None = None
    dist_mm: float | None = None
    gaze_overlap: float | None = None
    g_eye_left: list[CartSys3d] | None = None
    g_eye_right: list[CartSys3d] | None = None
    g_nose: list[CartSys3d] | None = None
    g_head_position: list[CartSys3d] | None = None
    g_gaze: list[CartSys3d] | None = None


@dataclass
class SstMeta(object):
    """Available information about tracked sounds.

    Args:
        id (int): ID per separable sound source, reused.
        activity (float): Activity of signal (0 to 1).
        loc (CartSys3d): Spacial source of sound.
        is_dynamic (bool): If track is dynamic or statically defined.
    """

    id: int
    activity: float
    loc: CartSys3d
    is_dynamic: bool


@dataclass
class PerceptionData(object):
    """Class containing infomation sent via perception socket.

    The data contains the latest information about the perceived surroundings of
    the robot.

    Args:
        time (int): Timestap of image taken as basis for persons
        persons (list[Person]): List of detected persons.
        sst_time_latest (int): Timestamp of audio taken as basis for sst_latest
        sst_tracks_latest (list[SstMeta]): Most current list of detected sound sources.
    """

    time: int = 0
    persons: List[Person] = field(default_factory=list)
    sst_time_latest: int = 0
    sst_tracks_latest: List[SstMeta] = field(default_factory=list)


@dataclass
class PerceptionId(object):
    """Class containing information about stored ids.

    If an entry is persistent, it is retained in storage. This is true even
    after a restart.

    Args:
        uid (int): Unique id of entry
        is_persistent (bool): If entry is persistent in storage
    """

    uid: int = 0
    is_persistent: bool = False


@dataclass
class Position:
    """Position of the robot base in Cartesian frame (meters)."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Orientation:
    """Orientation of the robot base as quaternions (x, y, z, w)."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0


@dataclass
class Velocity:
    """Velocity of the robot base in Cartesian frame (m/s and rad/s)."""

    linear_x: float = 0.0
    linear_y: float = 0.0
    linear_z: float = 0.0
    angular_x: float = 0.0
    angular_y: float = 0.0
    angular_z: float = 0.0


@dataclass
class OdometryData:
    """Odometry state of the robot."""

    time: int = 0
    position: Position | None = None
    orientation: Orientation | None = None
    velocity: Velocity | None = None
