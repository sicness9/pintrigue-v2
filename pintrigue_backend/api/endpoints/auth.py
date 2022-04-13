# auth endpoints

from datetime import timedelta
import logging

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..auth.auth_utils import authenticate_user, create_access_token, get_current_active_user
from pintrigue_backend.schemas.schemas import Token, UserWithID
from pintrigue_backend.database.mongodb.db import login


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)


@router.post("/login/access-token", response_model=Token)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    logging.info("login_access_token: authenticating user")
    user = authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # elif not utils.is_active(user):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=30)

    jwt = create_access_token(
                user['user_id'], expires_delta=access_token_expires
            )
    try:
        login(user_id=user['user_id'], jwt=jwt)
        response_object = {
            "access_token": jwt,
            "token_type": "bearer",
        }
        return response_object
    except Exception as e:
        return {"error": e}


@router.get("/me", response_model=UserWithID)
async def get_users_me(current_user: UserWithID = Depends(get_current_active_user)) -> any:
    return current_user
