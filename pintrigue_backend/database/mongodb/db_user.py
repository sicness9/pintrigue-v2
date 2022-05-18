# mongodb database functions

import os
from datetime import datetime
from random import choice

from dotenv import load_dotenv
from uuid import uuid4, UUID

from pymongo import MongoClient, WriteConcern, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

load_dotenv()

"""
Mongodb database set up
"""

PINTRIGUE_DB_URI = os.getenv("PINTRIGUE_DB_URI")
PINTRIGUE_DB_NAME = os.getenv("PINTRIGUE_DB_NAME")

db = MongoClient(
    PINTRIGUE_DB_URI,
    uuidRepresentation='standard',
    maxPoolSize=100,
    wTimeoutMS=2500
)[PINTRIGUE_DB_NAME]

"""
User collection
"""

users = db.users  # users collection
sessions = db.sessions  # sessions collection, used to handle sessions when a user signs in


def login(user_id, jwt):
    """
    Creates an entry in the sessions collection on sign in
    :param user_id:
    :param jwt:
    :return:
    """
    try:
        db.sessions.update_one(
            {"user_id": UUID(user_id)},
            {"$set": {"jwt": jwt}},
            upsert=True
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


def verify_active_session(user_id):
    try:
        db.sessions.find_one(
            {"user_id": UUID(user_id)}
        )
        return {"success": True}
    finally:
        return {"success": False}


# look up a single user
def get_user(username):
    """
    Query users collection with username.
    No _id in response
    :param username:
    :return:
    """
    return db.users.find_one({'username': username}, {"_id": 0})


# look up a user by email
def get_user_by_email(email):
    """
    Query users collection with email
    :param email:
    :return:
    """
    return db.users.find_one({'email': email}, {"_id": 0})


# look up a user by email
def get_user_by_id(user_id):
    return db.users.find_one({'user_id': UUID(user_id)}, {"_id": 0})


# look for all users in db
def get_all_users():
    """
    Using a cursor, query db for all users.
    No _id in response
    :return:
    """
    list_of_users = []
    cursor = users.find({}, {"_id": 0})
    for document in cursor:
        list_of_users.append(document)
    return list_of_users


# get a user's user_id
def get_user_id(username):
    """
    Query for a user_id using a username
    :param username:
    :return:
    """
    return db.users.find_one({'username': username}, {'_id': 0, "user_id": 1}).inserted_id


# create a user
def create_user(name, username, email, hashedpw, image_id):
    """
    Take the following params and insert doc into the 'users' collection to create a user
    :param image_id:
    :param email:
    :param name:
    :param username:
    :param hashedpw:
    """

    uuid_object = uuid4()

    try:
        db.users.insert_one(
            {
                "user_id": uuid_object,
                "name": name,
                "email": email,
                "username": username,
                "password": hashedpw,
                "image_id": image_id,
            }, WriteConcern(w='majority')  # durable writes with majority WriteConcern
        )
        return {"success": True}
    except DuplicateKeyError:
        return {"error": "A user with the given email already exists."}


# update username
def update_username(user_id, current_username, new_username):
    """
    User the user_id and current_username to query the correct user document then, update the username
    :param user_id:
    :param current_username:
    :param new_username:
    :return:
    """
    print(f"Received info - {user_id} - {current_username} - {new_username}")
    try:
        db.users.update_one(
            {"user_id": UUID(user_id), "username": current_username},
            {"$set": {"username": new_username}}
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


# update password
def update_password(user_id, new_password):
    """
    Match customer by user_id.Use the newly entered password to update in db
    :param new_password:
    :param user_id:
    :return:
    """
    try:
        db.users.update_one(
            {"user_id": UUID(user_id)},
            {"$set": {"password": new_password}}
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


# delete a user
def delete_user(user_id, email):
    """
    - Take the given email and delete a user from the 'users' collection
    - Verify the user is deleted by using the get_user function
    :param user_id:
    :param email:
    :return:
    """

    try:
        db.users.delete_one({"user_id": UUID(user_id), "email": email})

        # check if the user exists in 'users' collection to confirm delete was successful
        if get_user(email) is None:
            return {"success": True}
        else:
            raise ValueError("Deletion unsuccessful")
    except Exception as e:
        return {"error": e}
