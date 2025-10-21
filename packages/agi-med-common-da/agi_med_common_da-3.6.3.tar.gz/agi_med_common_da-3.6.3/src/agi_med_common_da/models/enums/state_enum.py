from enum import StrEnum, auto


class StateEnum(StrEnum):
    EMPTY = auto()
    COLLECTION = auto()
    READINESS = auto()
    FINAL = auto()
    ERROR = auto()
