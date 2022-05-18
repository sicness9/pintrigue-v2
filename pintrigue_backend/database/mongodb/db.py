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


""""
PostedBy collection
"""

postedby = db.postedby  # postedby collection


def create_posted_by(user):
    """
    Create a collection to track postedby

    TODO: Might get rid of this collection, will see if it is necessary
    :param user:
    :return:
    """
    try:
        db.postedby.insert_one(
            {
                "posted_by": user.username
            }
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}



