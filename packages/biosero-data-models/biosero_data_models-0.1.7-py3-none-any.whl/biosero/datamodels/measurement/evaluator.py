from enum import Enum

class Evaluator(Enum):
    Equal = "="
    NotEqual = "≠"
    LessThan = "<"
    GreaterThan = ">"
    GreaterThanOrEqual = "≥"
    LessThanOrEqual = "≤"
    # Contains = "contains"
    # StartsWith = "starts with"
    # EndsWith = "ends with"
    # After = "after (time)"
    # Before = "before (time)"
    # SameTime = "equals (time)"