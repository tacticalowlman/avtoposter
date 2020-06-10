import datetime

from pydantic.dataclasses import dataclass


@dataclass
class ScheduledPost:
    text: str
    post_time: datetime.datetime
    is_posted: bool

    def __post_init__(self):
        self.post_time = datetime.datetime.fromtimestamp(self.post_time)
        print(self.post_time.tzinfo)
