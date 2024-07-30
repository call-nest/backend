import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.orm import Posts, User, Collaborations
from app.database.repository import  CollaborateRepository
from app.schema.request import CollaborationRequest
from app.schema.response import CollaborationResponse

router = APIRouter(prefix="/collaborations")


@router.post("/", status_code=201)
def create_collaboration(request: CollaborationRequest, db: Session = Depends(get_db),
                         coll_repo: CollaborateRepository = Depends()):
    post = db.query(Posts).filter(Posts.id == request.post_id).first()
    user = db.query(User).filter(User.id == request.user_id).first()

    if not post or not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글 또는 사용자입니다.")

    collaboration = Collaborations(
        post_id=request.post_id,
        user_id=request.user_id,
        created_at=datetime.datetime.now()
    )

    coll_repo.create_collaborate(
        post_id=request.post_id,
        user_id=request.user_id,
    )

    return CollaborationResponse(
        id=collaboration.id,
        post_id=collaboration.post_id,
        user_id=collaboration.user_id,
        created_at=collaboration.created_at.isoformat(),
        is_reject=collaboration.is_reject,
        is_accepted=collaboration.is_accepted,
        is_canceled=collaboration.is_canceled
    )
