# mongodb comment database functions

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
Comment collection
"""

comments = db.comments  # comments collection


def create_comment(pin_id, posted_by, comment):
    print(f"Received comment data: {pin_id} - {posted_by} - {comment}")
    """
    With the given parameters, enter a comment doc into the 'comments' collection
    :param pin_id:
    :param posted_by:
    :param comment:
    """

    uuid_object = uuid4()

    try:
        db.comments.insert_one(
            {
                "comment_id": uuid_object,
                "pin_id": UUID(pin_id),
                "posted_by": posted_by,
                "comment": comment,
                "created_at": datetime.utcnow()
            }, WriteConcern(w="majority")  # durable writes
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


def update_comment(comment_id, comment):
    """
    With the given information, update a comment on a pin
    :param comment_id:
    :param comment:
    """
    try:
        db.comments.update_one(
            {
                "comment_id": UUID(comment_id)
            },
            {"$set": {"comment": comment, "date": datetime.utcnow()}}
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


def delete_comment(comment_id):
    """
    verify the comment_id and the user's email to delete a comment
    :param comment_id:
    """
    try:
        db.comments.delete_one(
            {
                "comment_id": UUID(comment_id)
            }
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


# for testing purposes only
def get_random_comment():
    list_of_comments = []
    cursor = db.comments.find({}, {"_id": 0})
    for document in cursor:
        list_of_comments.append(document)
    return choice(list_of_comments)


# for testing purposes only
def get_comment(pin_id, posted_by, comment):
    return db.comments.find_one({"pin_id": UUID(pin_id), "posted_by": posted_by, "comment": comment}, {"_id": 0})
