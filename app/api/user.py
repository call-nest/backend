from fastapi import APIRouter, Depends, HTTPException

from app.cache import redis_client
from app.database.orm import User
from app.database.repository import UserRepository
from app.schema.request import SignUpRequest, CreateOTPRequest, VerifyNicknameRequest, LoginRequest, InterestsRequest, \
    VerifyOTPRequest, UpdateProfileRequest, DeleteUserRequest
from app.schema.response import UserSchema, JWTResponse, UserInfoResponse
from app.security import get_access_token
from app.service.user import UserService

router = APIRouter(prefix="/users")


@router.post("/signup", status_code=201)
def user_sign_up(request: SignUpRequest, user_repo: UserRepository = Depends(), user_service: UserService = Depends()):
    user: User or None = user_repo.get_user_by_email(email=request.email)

    if user:
        raise HTTPException(status_code=400, detail="이미 존재하는 계정입니다.")

    hashed_password = user_service.hash_password(plain_password=request.password)
    user = User.create(email=request.email, nickname=request.nickname, password=hashed_password)
    user = user_repo.save_user(user=user)
    return {"message": "회원가입이 가능합니다.", "data": {"user": UserSchema.from_orm(user)}}


@router.post("/nickname/verify")
def verify_nickname(request: VerifyNicknameRequest, user_repo: UserRepository = Depends()):
    user = user_repo.get_user_by_nickname(nickname=request.nickname)
    if user:
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다.")

    return {"message": "사용 가능한 닉네임입니다."}


@router.post("/email/otp")
def create_otp_handler(request: CreateOTPRequest, user_service: UserService = Depends()):
    otp = user_service.create_otp()
    user_service.send_email_to_user(request.email, otp)
    redis_client.set(name=request.email, value=otp, ex=3 * 60)
    return {"otp": otp}


@router.post("/email/otp/verify")
def verify_otp_handler(request: VerifyOTPRequest):
    saved_otp = redis_client.get(name=request.email)
    if not saved_otp:
        raise HTTPException(status_code=404, detail="OTP 코드가 만료되었습니다.")

    if int(saved_otp) != request.otp:
        raise HTTPException(status_code=400, detail="OTP 코드가 일치하지 않습니다.")

    return {"message": "인증이 완료되었습니다."}


@router.post("/login")
def user_login(request: LoginRequest, user_repo: UserRepository = Depends(),
               user_service: UserService = Depends()):
    user: User or None = user_repo.get_user_by_email(email=request.email)

    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 계정입니다.")

    verified_passwd = user_service.varify_password(plain_password=request.password, hashed_password=user.password)

    if not verified_passwd:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    access_token = user_service.create_jwt(email=user.email)

    return {"message": "로그인에 성공하였습니다.",
            "data": {"token": JWTResponse(access_token=access_token), "user": UserSchema.from_orm(user)}}


@router.delete("/{user_id}/delete")
def delete_user(user_id: int, delete_req: DeleteUserRequest, user_repo: UserRepository = Depends(),
                user_service: UserService = Depends()):
    user = user_repo.get_user_by_id(user_id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 계정입니다.")

    verified_passwd = user_service.varify_password(plain_password=delete_req.password, hashed_password=user.password)

    if not verified_passwd:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    user_repo.delete_user(user=user)

    return {"message": "계정이 삭제되었습니다."}


@router.post("/{user_id}/interests")
def user_interests(user_id: int, interests_request: InterestsRequest, user_repo: UserRepository = Depends()):
    user = user_repo.get_user_by_id(user_id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 계정입니다.")

    user = user_repo.add_interests(user=user, interests=interests_request.interests)
    return {"message": "관심사가 등록되었습니다.", "data": {"user": UserSchema.from_orm(user)}}


@router.get("/{user_id}/user_info")
def get_user(user_id: int, user_repo: UserRepository = Depends()):
    user = user_repo.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 계정입니다.")

    user_info = UserInfoResponse.from_orm(user)
    return {"message": "유저 정보입니다.", "data": {"user": user_info}}


@router.get("/{user_id}/interests")
def get_user_interests(user_id: int, user_repo: UserRepository = Depends()):
    user = user_repo.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 계정입니다.")

    return {"message": "유저의 관심사입니다.", "data": {"interests": [interest.interest for interest in user.interests]}}


@router.patch("/{user_id}/update_profile")
def update_profile(user_id: int, update_req: UpdateProfileRequest, user_repo: UserRepository = Depends()):
    user = user_repo.get_user_by_id(user_id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 계정입니다.")

    if update_req.nickname:
        user.nickname = update_req.nickname
    if update_req.profile_img:
        user.profile_img = update_req.profile_img
    if update_req.introduce:
        user.introduce = update_req.introduce
    if update_req.interests:
        user_repo.add_interests(user=user, interests=update_req.interests)

    user_repo.save_user(user=user)

    return {"message": "프로필이 수정되었습니다.", "data": {"user": UserSchema.from_orm(user)}}
