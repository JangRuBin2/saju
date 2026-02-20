from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class CalendarType(str, Enum):
    SOLAR = "solar"
    LUNAR = "lunar"
