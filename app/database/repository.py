from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.orm import User, Interests, Posts


class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()
        self.session.refresh(instance=user)
        return user

    def get_user_by_email(self, email: str) -> User or None:
        return self.session.scalar(select(User).where(User.email == email))

    def get_user_by_nickname(self, nickname: str) -> User or None:
        return self.session.scalar(select(User).where(User.nickname == nickname))

    def get_user_by_id(self, user_id: int) -> User or None:
        return self.session.scalar(select(User).where(User.id == user_id))

    def delete_user(self, user: User):
        self.session.delete(user)
        self.session.commit()

    def add_interests(self, user: User, interests: list) -> User:
        user.interests.clear()

        for interest_name in interests:
            interest = self.session.query(Interests).filter(Interests.interest == interest_name).first()

            if interest:
                user.interests.append(interest)
            else:
                new_interest = Interests(interest=interest_name)
                user.interests.append(new_interest)

        self.session.commit()
        self.session.refresh(instance=user)
        return user


class PostRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def create_post(self, post: Posts) -> Posts:
        self.session.add(instance=post)
        self.session.commit()
        self.session.refresh(instance=post)
        return post

    def get_post_by_user_id(self, user_id: int) -> list[Posts]:
        result = self.session.execute(select(Posts).where(Posts.writer == user_id)).scalars().all()
        return result

    def get_post_by_id(self, post_id: int) -> Posts or None:
        return self.session.scalar(select(Posts).where(Posts.id == post_id))


class CollaborateRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def create_collaborate(self, post_id: int, user_id: int) -> Posts:
        post = self.session.query(Posts).filter(Posts.id == post_id).first()
        user = self.session.query(User).filter(User.id == user_id).first()

        self.session.commit()
        self.session.refresh(instance=post)
        return post
