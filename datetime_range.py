from dataclasses import dataclass
import datetime as dt


@dataclass
class DateTimeRange:
    start: dt.datetime | dt.time
    end: dt.datetime | dt.time

    def __contains__(self, item: dt.datetime | dt.time) -> bool:
        if type(item) is type(self.start):
            return self.start <= item <= self.end
        elif type(self.start) is dt.datetime and type(item) is dt.time:
            return self.start.time() <= item <= self.end.time()
        elif type(self.start) is dt.time and type(item) is dt.datetime:
            return self.start <= item.time() <= self.end
        else:
            raise ValueError(f'Wrong types of arguments operation: {type(item)} in {type(self)}')