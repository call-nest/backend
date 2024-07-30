import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.orm import User, Posts
from app.database.repository import PostRepository
from app.schema.request import CreatePostRequest
from app.schema.response import PostResponse, PostListResponse, Pagination, UserPostResponse, PostUserResponse

router = APIRouter(prefix="/posts")


@router.post("/create", response_model=PostResponse)
def create_post(request: CreatePostRequest, db: Session = Depends(get_db), post_repo: PostRepository = Depends()):
    user = db.query(User).filter(User.id == request.writer).first()

    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")

    post = Posts(
        title=request.title,
        content=request.content,
        writer=request.writer,
        created_at=datetime.datetime.now(),
        is_recruit=request.is_recruit
    )

    post = post_repo.create_post(post=post)

    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        writer_nickname=user.nickname,
        is_recruit=post.is_recruit,
        created_at=post.created_at.isoformat(),  # 문자열로 변환
        updated_at=post.updated_at.isoformat() if post.updated_at else None,  # 문자열로 변환
        is_deleted=post.is_deleted
    )


@router.get("/all", response_model=PostListResponse)
def get_all_posts(
        page: int = Query(1, ge=1, description="Page Number"),
        page_size: int = Query(100, ge=1, le=100, description="Page Size"),
        db: Session = Depends(get_db)
):
    total_posts = db.query(Posts).count()
    if total_posts == 0:
        raise HTTPException(status_code=404, detail="No posts found")

    posts = db.query(Posts).offset((page - 1) * page_size).limit(page_size).all()

    # 응답을 위한 PostResponse 리스트 생성
    response = []
    for post in posts:
        writer = db.query(User).filter(User.id == post.writer).first()
        if writer is None:
            raise HTTPException(status_code=404, detail=f"User with id {post.writer} not found")

        response.append(PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            writer_nickname=writer.nickname,
            is_recruit=post.is_recruit,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat() if post.updated_at else None,
            is_deleted=post.is_deleted,
        ))

    return PostListResponse(
        message="success!",
        data=response,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_posts=total_posts,
            total_pages=(total_posts + page_size - 1) // page_size
        )
    )


@router.get("/{user_id}/posts", response_model=UserPostResponse)
def get_user_posts(user_id: int, post_repository: PostRepository = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")

    posts = post_repository.get_post_by_user_id(user_id)

    response = []
    for post in posts:
        response.append(PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            writer_nickname=user.nickname,
            is_recruit=post.is_recruit,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat() if post.updated_at else None,
            is_deleted=post.is_deleted,
        ))

    if not response:
        return UserPostResponse(msg="게시물이 없습니다.", data=response)

    return UserPostResponse(msg="success!", data=response)


@router.get("/{post_id}", response_model=PostUserResponse)
def get_post(post_id: int, db: Session = Depends(get_db), post_repo: PostRepository = Depends()):
    post = post_repo.get_post_by_id(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다.")

    writer = db.query(User).filter(User.id == post.writer).first()

    if not writer:
        raise HTTPException(status_code=404, detail="작성자를 찾을 수 없습니다.")

    return PostUserResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        writer_nickname=writer.nickname,
        writer=writer.id,
        is_recruit=post.is_recruit,
        created_at=post.created_at.isoformat(),
        updated_at=post.updated_at.isoformat() if post.updated_at else None,
        is_deleted=post.is_deleted
    )


