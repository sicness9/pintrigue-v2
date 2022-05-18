# mongodb database save functions

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
Save collection
"""

saves = db.saves  # saves collection


def add_save(posted_by, user_id):
    """
    When someone saves a pin, insert into 'saves' collection
    posted_by is the maker of the post
    user_id is the current user making the save
    :param posted_by:
    :param user_id:
    """

    uuid_object = uuid4()

    try:
        db.saves.insert_one(
            {
                "save_id": uuid_object,
                "posted_by": posted_by,
                "user_id": user_id
            }
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


def remove_save(save_id):
    """
    Remove a save from collection
    :param save_id:
    """

    response = db.saves.delete_one(
        {
            "save_id": UUID(save_id),
        }
    )
    return response
