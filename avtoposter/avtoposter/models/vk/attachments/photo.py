import datetime
import typing
from pydantic.dataclasses import dataclass


@dataclass
class PhotoSize:
    photo_type: str
    url: str
    width: int
    height: int


@dataclass
class Photo:
    id: int
    album_id: int
    owner_id: int
    user_id: int
    text: str
    date: datetime.datetime
    sizes: typing.List[PhotoSize]
    width: int
    height: int
