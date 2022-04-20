import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Union
import logging

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi.encoders import jsonable_encoder

from pintrigue_backend.database.mongodb.db import get_user, verify_active_session, get_user_by_id
from pintrigue_backend.schemas.schemas import TokenData, Token, User, UserWithID

load_dotenv()

# JWT variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
TOKEN_URL = os.getenv("TOKEN_URL")

oauth2 = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# verify hashed password with the plain
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# has the entered password
def get_password_hash(password):
    return pwd_context.hash(password)


# authenticate user by verifying the given password with username and hashed password
def authenticate_user(username: str, password: str) -> any:
    logging.info(f"Authenticate_user: authenticating {username}")
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user


# check if the user is active
# def is_active(user: schema.User) -> bool:
#     return user.disabled


# create access token function
def create_access_token(subject: Union[str, any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# get the current user
def get_current_user(token: str = Depends(oauth2)) -> any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # token_data = TokenData(**payload)
        logging.info("Get_current_user: Fetching user")
        user_id: str = payload.get("sub")
        print(f"User_id fetched from payload - {user_id}")
        user = get_user_by_id(user_id=user_id)
    except JWTError:
        raise credentials_exception
    return user


def get_current_active_user(current_user: UserWithID = Depends(get_current_user)):
    if verify_active_session(current_user["user_id"]):
        return current_user
