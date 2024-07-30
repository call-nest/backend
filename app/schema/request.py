from typing import Optional

from pydantic import BaseModel


class SignUpRequest(BaseModel):
    email: str
    nickname: str
    password: str


class CreateOTPRequest(BaseModel):
    email: str


class VerifyOTPRequest(BaseModel):
    email: str
    otp: int


class VerifyNicknameRequest(BaseModel):
    nickname: str


class LoginRequest(BaseModel):
    email: str
    password: str


class DeleteUserRequest(BaseModel):
    password: str


class InterestsRequest(BaseModel):
    interests: list[str]


class UserInfoRequest(BaseModel):
    id: int
    email: str
    nickname: str
    profile_img: Optional[str]
    introduce: Optional[str]
    interests: list[str]


class UpdateProfileRequest(BaseModel):
    nickname: str or None
    profile_img: str or None
    introduce: str or None
    interests: list[str]


class CreatePostRequest(BaseModel):
    title: str
    content: str
    writer: int
    is_recruit: bool


class CollaborationRequest(BaseModel):
    post_id: int
    user_id: int