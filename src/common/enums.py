from enum import Enum


class AsMinutes(int, Enum):
    MINUTE = 1
    HOUR = 60
    DAY = 60 * 24
    YEAR = 60 * 24 * 365


class AuthMethod(Enum):
    UNDEFINED = 0
    TEST = 1
    DEMO = 2


class ApiMode(Enum):
    UNDEFINED = 0
    DEV = 1
    PROD = 9
