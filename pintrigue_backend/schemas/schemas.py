from typing import List, Optional, Dict
from datetime import datetime

# from bson import ObjectId
from pydantic import BaseModel, Field


# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate
#
#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid objectid")
#         return ObjectId(v)
#
#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")


"""
User schemas
"""


class User(BaseModel):
    name: str = Field(...)
    email: str = Field(...)
    username: str = Field(...)
    image_id: str = Field(...)


class UserUsernameOnly(BaseModel):
    username: str = Field(...)


class UserCreate(User):
    password: str = Field(...)


class UserWithID(User):
    user_id: str = Field(...)


class UserInDB(UserCreate):
    # id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    hashedpw: str = Field(...)
    user_id: str = Field(...)

    # class Config:
    #     allow_population_by_field_name = True
    #     arbitrary_types_allowed = True
    #     json_encoders = {ObjectId: str}


"""
Token schemas
"""


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


"""
Posted_By schema
"""


class PostedBy(BaseModel):
    username: str


"""
Comment schema
"""


class Comment(BaseModel):
    posted_by: str
    comment: str
    pin_id: str


class CommentInDB(Comment):
    created_at: str
    comment_id: str


"""
Save schemas
"""


class Save(BaseModel):
    posted_by: str
    user_id: str


class SaveInDB(Save):
    save_id: str


"""
Pin schemas
"""


class Pin(BaseModel):
    title: str
    about: str
    category: str
    image_id: str


class PinCreate(Pin):
    pass


class PinInDB(PinCreate):
    posted_by: str
    comments: List[Comment] = None
    pin_id: str
    created_at: str
