# tests for user functions

import os
from dotenv import load_dotenv

from pintrigue_backend.database.mongodb.db import create_user, update_username, get_user_by_email, delete_user, \
    update_password
from pintrigue_backend.api.auth.auth_utils import get_password_hash

import pytest
from faker import Faker

load_dotenv()

# env variables
BUCKET_NAME = os.getenv('BUCKET_NAME')

fake = Faker()


class TestUser:
    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password = password


@pytest.fixture
def create_test_user():
    fake_profile = fake.simple_profile()
    image_id = f"https://storage.googleapis.com/{BUCKET_NAME}/No_image_available.svg.png"
    create_user(name=fake_profile['name'], username=fake_profile['username'], email=fake_profile['mail'],
                hashedpw=get_password_hash('test123'), image_id=image_id)
    user = get_user_by_email(email=fake_profile['mail'])
    return user


class TestUserClass:

    def test_create_user(self):
        """
        Tests the create_user function using Faker for fake profile info then, deletes the newly created user to save db
        space
        :return:
        """
        fake_profile = fake.simple_profile()
        print("Test - Fake profile object: ", fake_profile)
        user = TestUser(name=fake_profile['name'], username=fake_profile['username'], email=fake_profile['mail'],
                        password="test123")
        image_id = f"https://storage.googleapis.com/{BUCKET_NAME}/No_image_available.svg.png"
        assert create_user(name=user.name,
                           username=user.username,
                           email=user.email,
                           hashedpw=get_password_hash(user.password),
                           image_id=image_id) == {"success": True}
        new_user = get_user_by_email(email=user.email)
        # delete the newly created account to stop filling db with test info
        delete_user(user_id=str(new_user['user_id']), email=new_user['email'])  # clean up

    def test_update_username(self, create_test_user):
        """
        Tests the update_username function, takes the newly created User from create_test_user and then delete after the
        test
        :param create_test_user:
        :return:
        """
        print("Test- test_update_username - User profile received: ", create_test_user)
        assert update_username(user_id=str(create_test_user['user_id']),
                               current_username=create_test_user['username'],
                               new_username=f"updated_{create_test_user['username']}"
                               ) == {"success": True}
        delete_user(user_id=str(create_test_user['user_id']), email=create_test_user['email'])  # clean up

    def test_update_password(self, create_test_user):
        """
        Tests the update_password function, takes the newly created User from create_test_user and then deletes it after
        the test
        :param create_test_user:
        :return:
        """
        print("Test- test_update_password - User profile received: ", create_test_user)
        assert update_password(user_id=str(create_test_user['user_id']),
                               new_password=get_password_hash('updated_password1')) == {"success": True}
        delete_user(user_id=str(create_test_user['user_id']), email=create_test_user['email'])  # clean up

    def test_delete_user(self, create_test_user):
        """
        Tests the delete_user function, takes the newly created User from create_test_user
        :param create_test_user:
        :return:
        """
        print("Test- test_delete_user - User profile received: ", create_test_user)
        assert delete_user(user_id=str(create_test_user['user_id']), email=create_test_user['email'])
