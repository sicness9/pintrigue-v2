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
            query = {"category": {"$in": filters["category"]}}
        elif "posted_by" in filters:
            query = {"posted_by": {"$in": filters["posted_by"]}}
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
