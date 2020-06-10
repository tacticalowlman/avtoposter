import datetime
from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class Comments:
    count: int
    can_post: bool
    groups_can_post: bool
    can_close: Optional[bool] = None
    can_open: Optional[bool] = None


@dataclass
class Likes:
    count: int
    user_likes: bool = False
    can_like: bool = False
    can_publish: bool = False


@dataclass
class Reposts:
    count: int
    user_reposted: bool = False


@dataclass
class Views:
    count: int


@dataclass
class PostSource:
    type: str
    platform: Optional[str] = None
    data: Optional[str] = None
    url: Optional[str] = None


@dataclass
class Post:
    id: int
    owner_id: int
    from_id: int
    date: datetime.datetime
    text: str
    comments: Comments
    likes: Likes
    reposts: Reposts
    post_type: str
    marked_as_ads: bool
    post_source: PostSource
    # attachments: Optional[List[Union[attachments.Video, attachments.PostedPhoto, attachments.Photo]]] = None
    views: Optional[Views] = None
    attachments: Optional[list] = None
    created_by: Optional[int] = None
    friends_only: Optional[bool] = None
    reply_owner_id: Optional[int] = None
    reply_post_id: Optional[int] = None
    is_pinned: Optional[bool] = False
    edited: Optional[datetime.datetime] = None

    def __post_init__(self):
        self.date = datetime.datetime.fromtimestamp(int(self.date))
