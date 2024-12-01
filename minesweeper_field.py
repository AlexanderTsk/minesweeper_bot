from dataclasses import dataclass
from enum import Enum

class FieldType(Enum):
    UNKNOWN = 'x'
    EMPTY = '0'
    ONE = '1'
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    BOMB = '*'

@dataclass
class MinesweeperField:
    type: FieldType
    x: int
    y: int