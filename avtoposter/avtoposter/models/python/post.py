import datetime
from dataclasses import dataclass


@dataclass
class Post:
    post_time: datetime.datetime
    chat_id: int
    post_id: int
