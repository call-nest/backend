from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nickname = Column(String(50), index=True, nullable=False)
    password = Column(String(255), nullable=False)
    profile_img = Column(String(255), nullable=True)
    introduce = Column(Text, nullable=True)
    # 접근 권한
    # 활성화 (본인이 삭제할 시 int 1, 운영자 삭제할 시 int 0)
    # 만든 시각
    # 수정한 시각

    # secondary = 연결 테이블, backref = 연결 테이블을 통해 역참조 (양방향)
    interests = relationship("Interests", secondary="user_interests", backref="users", cascade="all, delete",
                             passive_deletes=True)

    posts = relationship("Posts", backref="author", cascade="all, delete-orphan", passive_deletes=True)

    collaborations = relationship("Collaborations", backref="user", cascade="all, delete-orphan", passive_deletes=True)

    likes = relationship("Likes", backref="user", cascade="all, delete-orphan", passive_deletes=True)

    @classmethod
    def create(cls, email: str, nickname: str, password: str) -> "User":
        return cls(
            email=email,
            nickname=nickname,
            password=password
        )


# many to many relationship 연결 테이블
user_interests = Table(
    "user_interests",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("interest_id", Integer, ForeignKey("interests.id", ondelete="CASCADE")),
    extend_existing=True
)


class Interests(Base):
    __tablename__ = "interests"
    id = Column(Integer, primary_key=True)
    interest = Column(String(50), unique=True, nullable=False)


class Posts(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    writer = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_recruit = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    collaborations = relationship("Collaborations", backref="post", cascade="all, delete-orphan", passive_deletes=True)
    likes = relationship("Likes", backref="post", cascade="all, delete-orphan", passive_deletes=True)


class Collaborations(Base):
    __tablename__ = "collaborations"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_accepted = Column(Boolean, default=False, nullable=False)  # 뭔가 user 쪽에 들어가야할 듯함
    is_rejected = Column(Boolean, default=False, nullable=False)  # 이것도
    is_canceled = Column(Boolean, default=False, nullable=False)  # 이것도
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)


class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False)
