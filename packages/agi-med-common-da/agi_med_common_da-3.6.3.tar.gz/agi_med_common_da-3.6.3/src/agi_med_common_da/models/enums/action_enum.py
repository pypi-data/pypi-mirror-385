from enum import StrEnum, auto


class ActionEnum(StrEnum):
    START = auto()
    ASK_FILE_AGAIN = auto()

    GREETING = auto()
    MODERATION = auto()
    ANSWER = auto()
    QUESTION = auto()
    CRITICAL = auto()
    MED_TEST_DECRYPTION = auto()

    DIAGNOSIS = auto()
    REPORT = auto()
    FINANCIAL_EXTRACTION = auto()
    FINAL = auto()
