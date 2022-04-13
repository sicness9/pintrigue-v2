# user endpoints

import os
from dotenv import load_dotenv
from typing import List

from fastapi import HTTPException, APIRouter
from fastapi.encoders import jsonable_encoder

from pintrigue_backend.schemas.schemas import User, UserCreate, UserWithID, UserInDB
from pintrigue_backend.database.mongodb.db import get_user, get_all_users, create_user, delete_user, update_username, \
    update_password, get_user_by_email, get_user_by_id
from ..auth.auth_utils import get_password_hash


load_dotenv()

# env variables
BUCKET_NAME = os.getenv('BUCKET_NAME')

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)


@router.get("/", response_model=List[UserWithID])
def api_get_users():
    """
    Endpoint for querying all users in the user's collection
    :return:
    """
    response = get_all_users()
    return jsonable_encoder(response)


@router.get("/<username>", response_model=UserWithID)
def api_get_user_by_username(username: str):
    """
    Search for a user by their username
    :param username:
    :return:
    """
    response = get_user(username)
    if response:
        return jsonable_encoder(response)
    raise HTTPException(404, f'No user found with the username {username}')


@router.post("/sign-up", response_model=UserWithID)
def api_user_signup(user: UserCreate) -> any:
    """
    Sign up end-point, take the following input to create a new user:
    email
    name
    password
    username
    :param user:
    """
    if user.email is None:
        raise HTTPException(400, "Missing email")
    elif user.name is None:
        raise HTTPException(400, "Missing name")
    elif user.username is None:
        raise HTTPException(400, "Missing username")
    elif len(user.username) < 5:
        raise HTTPException(400, "Username must be 5 or more characters.")
    elif len(user.username) > 14:
        raise HTTPException(400, "Username too long, must bne less than 14 characters")
    elif user.password is None:
        raise HTTPException(400, "Missing password")
    elif len(user.password) < 5:
        raise HTTPException(400, "Password must be 5 or more characters.")
    elif get_user(user.username):
        raise HTTPException(400, "Username already exists")
    elif user.email == get_user_by_email(user.email):
        raise HTTPException(400, "Email already in use")

    image_id = f"https://storage.googleapis.com/{BUCKET_NAME}/No_image_available.svg.png"
    response = create_user(name=user.name, username=user.username, email=user.email,
                           hashedpw=get_password_hash(user.password), image_id=image_id)
    if response:
        new_user = get_user(username=user.username)
        return jsonable_encoder(new_user)
    raise HTTPException(400, "Something went wrong")


@router.put("/update_username/<user_id>/<username>", response_model=User)
def api_update_user_username(current_username: str, new_username: str, user_id: str):
    """
    Using the entered parameters, update the username of a user. Query using the get_user() function to search for the
    user and send as response
    :param current_username:
    :param new_username:
    :param user_id:
    :return:
    """
    if current_username == new_username:
        raise HTTPException(400, "Username already in use")
    if len(new_username) > 12:
        raise HTTPException(400, "Username too long")
    if len(new_username) < 4:
        raise HTTPException(400, "Username too short")
    print(f"New info - user_id: {user_id} - current_username: {current_username} - new_username: {new_username}")
    response = update_username(user_id=user_id, current_username=current_username, new_username=new_username)

    if response:
        res = get_user(new_username)
        return jsonable_encoder(res)
    raise HTTPException(400, "Something went wrong")


@router.put("/password-change/<user_id>/")
def api_update_user_password(user_id: str, new_password: str) -> any:
    """
    Use the user_id to query the db and then enter the new_password into the doc
    :param user_id:
    :param new_password:
    :return:
    """
    if len(new_password) < 5:
        raise HTTPException(400, "Password must be 5 or more characters.")
    if len(new_password) > 12:
        raise HTTPException(400, "Password must be less than 12 characters.")

    response = update_password(user_id=user_id, new_password=get_password_hash(new_password))

    if response:
        return response
    raise HTTPException(400, "Something went wrong")


@router.delete("/<user_id>")
def api_delete_user(user_id: str, email: str):
    """
    Use the entered user_id and email to delete a user
    :param user_id:
    :param email:
    :return:
    """
    response = delete_user(user_id=user_id, email=email)
    if response:
        return response
    raise HTTPException(400, "Something went wrong")
