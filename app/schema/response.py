from typing import Optional

from pydantic import BaseModel
from sqlalchemy import DateTime

from app.database.orm import User


class UserSchema(BaseModel):
    id: int
    email: str
    nickname: str

    class Config:
        from_attributes = True


class JWTResponse(BaseModel):
    access_token: str


class UserInfoResponse(BaseModel):
    id: int
    email: str
    nickname: str
    profile_img: Optional[str]
    introduce: Optional[str]
    interests: list[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, user: User) -> "UserInfoResponse":
        interests = [interest.interest for interest in user.interests]
        return cls(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            profile_img=user.profile_img,
            introduce=user.introduce,
            interests=interests
        )


class UpdateProfileResponse(BaseModel):
    id: int
    email: str
    nickname: str
    profile_img: str or None = None
    introduce: str or None = None
    interests: list[str]


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    writer_nickname: str
    is_recruit: bool
    created_at: str
    updated_at: Optional[str] = None
    is_deleted: bool

    class Config:
        from_attributes = True


# 게시글 클릭 시 유저 아이디로 비교
class PostUserResponse(BaseModel):
    id: int
    title: str
    content: str
    writer_nickname: str
    writer: int
    is_recruit: bool
    created_at: str
    updated_at: Optional[str] = None
    is_deleted: bool


class UserPostResponse(BaseModel):
    msg: str
    data: list[PostResponse]


class Pagination(BaseModel):
    page: int
    page_size: int
    total_posts: int
    total_pages: int


class PostListResponse(BaseModel):
    message: str
    data: list[PostResponse]
    pagination: Pagination


class CollaborationResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    is_accepted: bool
    is_rejected: bool
    is_canceled: bool
    created_at: str
