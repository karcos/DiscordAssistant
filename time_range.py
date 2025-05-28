from dataclasses import dataclass
from datetime import time, datetime
from typing import Self

@dataclass
class TimeRange:
    start: time
    end: time

    def __contains__(self, item: time) -> bool:
        if type(item) != time:
            raise TypeError
        else:
            if self.start.hour <= item.hour <= self.end.hour:
                return True
            else:
                return False
