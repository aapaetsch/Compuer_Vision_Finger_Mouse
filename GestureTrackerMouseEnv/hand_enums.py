from enum import Enum
from typing import NamedTuple
import numpy as np


class Fingers(Enum):
    THUMB = 0
    INDEX = 1
    MIDDLE = 2
    RING = 3
    PINKY = 4

class FingerDistanceInfo(NamedTuple):
    length: float
    img: np.ndarray
    line_info: list
