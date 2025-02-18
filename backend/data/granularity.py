# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from functools import total_ordering
from typing import Literal
import pandas as pd

@total_ordering
class Granularity:
    ORDER = ["15min", "hour", "day", "week", "month"]

    def __init__(self, value):
        if value not in self.ORDER:
            raise ValueError(f"Invalid granularity: {value}")
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Granularity):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        raise ValueError(f"Invalid comparison: {other}")

    def __lt__(self, other):
        if isinstance(other, Granularity):
            return self.ORDER.index(self.value) < self.ORDER.index(other.value)
        elif isinstance(other, str):
            if other not in self.ORDER:
                raise ValueError(f"Invalid granularity: {other}")
            return self.ORDER.index(self.value) < self.ORDER.index(other)
        raise ValueError(f"Invalid comparison: {other}")

    def __str__(self):
        if self.value == "15min":
            return "fifteenMinBucket"
        return self.value
    
def adjust_date_and_granularity(start: str, end: str, granularity: str) -> tuple[pd.Timestamp, pd.Timestamp, Granularity]:
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    delta = end - start

    granularity = Granularity(granularity)
    # automatically adjust granularity if too coarse for specific start/end
    if delta.total_seconds() < 900 and granularity != "15min":
        print(f"Adjusting granularity from {granularity} to 15min")
        granularity = Granularity("15min")
    elif delta.total_seconds() < 3600 and granularity > "hour":
        print(f"Adjusting granularity from {granularity} to hour")
        granularity = Granularity("hour")
    elif delta.days < 1 and granularity > "day":
        print(f"Adjusting granularity from {granularity} to day")
        granularity = Granularity("day")
    elif delta.days < 7 and granularity > "week":
        print(f"Adjusting granularity from {granularity} to week")
        granularity = Granularity("week")

    return start, end, granularity