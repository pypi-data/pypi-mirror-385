from .going_description import GoingDescription as GoingDescription

class TurfGoingDescription(GoingDescription):
    HEAVY: int
    SOFT_TO_HEAVY: float
    SOFT: int
    YIELDING_TO_SOFT: float
    GOOD_TO_SOFT: int
    YIELDING: int
    GOOD_TO_YIELDING: float
    GOOD: int
    GOOD_TO_FIRM: int
    FIRM: int
    FIRM_TO_HARD: float
    HARD: int
    V = HEAVY
    HV = HEAVY
    HVY = HEAVY
    S = SOFT
    SFT = SOFT
    D = GOOD_TO_SOFT
    GS = GOOD_TO_SOFT
    YS = YIELDING_TO_SOFT
    Y = YIELDING
    YLD = YIELDING
    GY = GOOD_TO_YIELDING
    G = GOOD
    GD = GOOD
    GF = GOOD_TO_FIRM
    M = GOOD_TO_FIRM
    F = FIRM
    FM = FIRM
    FRM = FIRM
    HD = HARD
    HRD = HARD
