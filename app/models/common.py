from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class CalendarType(str, Enum):
    SOLAR = "solar"
    LUNAR = "lunar"


class PetSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class CareerConcernType(str, Enum):
    TIMING = "timing"
    DIRECTION = "direction"
    PROMOTION_VS_MOVE = "promotion_vs_move"
    STARTUP = "startup"
    BURNOUT = "burnout"
    SALARY = "salary"


class MarriageConcernType(str, Enum):
    WHEN = "when"
    READINESS = "readiness"
    COMPATIBILITY = "compatibility"
    FAMILY = "family"
    FINANCE = "finance"
    CHILDREN = "children"
