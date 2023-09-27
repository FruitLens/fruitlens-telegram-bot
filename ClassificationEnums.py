from enum import Enum


class FruitType(Enum):
    APPLE = "APPLE"
    BANANA = "BANANA"
    ORANGE = "ORANGE"


class FruitStage(Enum):
    RAM = "RAW"
    UNRIPE = "UNRIPE"
    RIPE = "RIPE"
    OVERRIPE = "OVERRIPE"
    ROTTEN = "ROTTEN"


class Confirmation(Enum):
    YES = "YES"
    NO = "NO"
