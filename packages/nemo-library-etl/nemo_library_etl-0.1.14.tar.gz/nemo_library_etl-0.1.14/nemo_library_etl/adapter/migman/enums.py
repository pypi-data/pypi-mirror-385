from enum import Enum


class MigManTransformStep(Enum):
    JOINS = "10_joins"
    DUPLICATES = "20_duplicates"
    NONEMPTY = "30_nonempty"
    