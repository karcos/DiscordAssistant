from dataclasses import dataclass
import datetime as dt


@dataclass(frozen=True)
class DateTimeRange:
    start: dt.datetime
    end: dt.datetime