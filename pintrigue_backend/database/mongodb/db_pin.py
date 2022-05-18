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
Pin collection
"""

pins = db.pins  # pins collection


# create a pin
def create_pin(title, about, category, image_id, posted_by):
    print(f"Pin information received: Title: {title} - About: {about} - Category: {category} - Image ID: {image_id} - \
    Posted By: {posted_by}")

    """
    With the given params, create a pin

    TODO: Need to get the image url from backblaze or google cloud
    :param title:
    :param about:
    :param category:
    :param image_id:
    :param posted_by:
    """

    uuid_object = uuid4()

    try:
        db.pins.insert_one(
            {
                "pin_id": uuid_object,
                "created_at": datetime.utcnow(),
                "title": title,
                "about": about,
                "category": category,
                "image_id": image_id,
                "posted_by": posted_by,
                "comments": []
            }, WriteConcern(w="majority")
        )
        # create_posted_by(posted_by)
        return {"success": True}
    except Exception as e:
        return {"error": e}


def query_sort_project(filters):
    """
    Using filter, use this function to build a query
    :param filters:
    :return:
    """

    query = {}
    sort = [("pin_id", DESCENDING)]

    if filters:
        if "text" in filters:
            query = {"$text": {"$search": filters["text"]}}
        elif "category" in filters:
            query = {"category": {"$in": [filters["category"]]}}
        elif "posted_by" in filters:
            query = {"posted_by": {"$in": [filters["posted_by"]]}}
    return query, sort


# function to enable paging for pins
def get_pins(filters, page, pins_per_page):
    query, sort = query_sort_project(filters)
    cursor = db.pins.find(query, {"_id": 0}).sort(sort)

    total_num_pins = 0
    if page == 0:
        total_num_pins = db.pins.count_documents(query)

    fetched_pins = cursor.skip(int(page * pins_per_page)).limit(pins_per_page)

    return list(fetched_pins), total_num_pins


# search function primarily used for the auto-complete search feature
def get_all_pins():
    list_of_pins = []
    cursor = pins.find({}, {"_id": 0, "comments": 0, "image_id": 0})
    for document in cursor:
        list_of_pins.append(document)
    return list_of_pins


def get_pins_by_category(categories):
    try:
        return list(db.pins.find({"category": {"$in": [categories]}}, {"title": 1, "posted_by": 1, "image_id": 1,
                                                                       "_id": 0}))
    except Exception as e:
        return {"Error": e}


def get_pin(title, posted_by):
    return db.pins.find_one(
        {"posted_by": posted_by, "title": title},
        {"_id": 0}
    )


def get_pin_by_id(pin_id):
    """
    Using a pipeline, join two collections to get a pin and the comments associated with it
    :param pin_id:
    """

    pipeline = [
        {
            '$match': {
                'pin_id': UUID(pin_id)
            }
        }, {
            '$lookup': {
                'from': 'comments',
                'let': {
                    'pin_id': '$pin_id'
                },
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$pin_id', '$$pin_id'
                                ]
                            }
                        }
                    }, {
                        '$project': {
                            '_id': 0
                        }
                    }
                ],
                'as': 'comments'
            }
        }, {
            '$sort': {
                'created_at': -1
            }
        }, {
            '$project': {
                '_id': 0
            }
        }
    ]

    pin = db.pins.aggregate(pipeline).next()
    return pin


def get_popular_pin_categories(limit):
    """
    This function returns the top 8 most created pin categories
    :return:
    """
    pipeline = [
        {
            '$project': {
                'category': 1,
                'image_id': 1,
                'posted_by': 1,
                '_id': 0
            }
        }, {
            '$group': {
                '_id': '$category',
                'totalPins': {
                    '$count': {}
                }
            }
        }, {
            '$sort': {
                'totalPins': -1
            }
        }, {
            '$limit': limit
        }
    ]
    pin = list(db.pins.aggregate(pipeline))
    return pin


def update_pin_title(pin_id, title):
    """
    Update the title of a pin
    :param pin_id:
    :param title:
    """
    try:
        db.pins.update_one(
            {
                "pin_id": UUID(pin_id)
            },
            {"$set": {"title": title}}
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


def update_pin_about(pin_id, about):
    """
    Update the about section of a pin
    :param pin_id:
    :param about:
    """
    try:
        db.pins.update_one(
            {
                "pin_id": UUID(pin_id)
            },
            {"$set": {"about": about}}
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


def update_pin_category(pin_id, category):
    """
    Update a category of a pin
    :param pin_id:
    :param category:
    """

    try:
        db.pins.update_one(
            {
                "pin_id": UUID(pin_id)
            },
            {"$set": {"category": category}}
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


def update_pin_image(pin_id, image_id):
    """
    Update a image of a pin
    :param pin_id:
    :param image_id:
    """
    try:
        db.pins.update_one(
            {
                "pin_id": UUID(pin_id)
            },
            {"$set": {"image_id": image_id}}
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


def delete_pin(pin_id):
    try:
        db.pins.delete_one(
            {"pin_id": UUID(pin_id)}
        )
        return {"success": True}
    except Exception as e:
        return {"error": e}


# for testing purposes only
def get_random_pin():
    list_of_pins = []
    cursor = db.pins.find({}, {"_id": 0})
    for document in cursor:
        list_of_pins.append(document)
    return choice(list_of_pins)