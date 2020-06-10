import datetime
from pydantic.dataclasses import dataclass


@dataclass
class Video:
    id: int
    owner_id: int
    title: str
    description: str
    duration: int
    photo_130: str
    photo_320: str
    photo_640: str
    photo_800: str
    photo_1280: str
    first_frame_130: str
    first_frame_320: str
    first_frame_640: str
    first_frame_800: str
    first_frame_1280: str
    date: datetime.datetime
    adding_date: datetime.datetime
    views: int
    comments: int
    player: str
    platform: str
    can_edit: bool
    can_add: bool
    is_private: bool
    access_key: str
    processing: bool
    live: bool
    upcoming: bool
    is_favourite: bool
