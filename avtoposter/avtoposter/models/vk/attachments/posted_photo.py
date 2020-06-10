from pydantic.dataclasses import dataclass


@dataclass
class PostedPhoto:
    id: int
    owner_id: int
    photo_130: str
    photo_640: str
