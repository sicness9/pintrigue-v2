# test functions for pins

import os
from dotenv import load_dotenv
from random import randint, choice
import pytest

from pintrigue_backend.database.mongodb.db_pin import create_pin, get_pins_by_category, get_random_pin, \
    get_pin_by_id, delete_pin, get_pin, update_pin_title, update_pin_about, update_pin_category
from pintrigue_backend.database.mongodb.db_user import get_all_users

load_dotenv()

# env variables
BUCKET_NAME = os.getenv('BUCKET_NAME')

category = ['Food', 'Games', 'Movies', 'Decoration', 'Housing', 'Random', 'DIY']


@pytest.fixture
def get_random_user():
    posted_by = get_all_users()
    return choice(posted_by)


@pytest.fixture
def get_rand_category():
    return choice(category)


class TestPinClass:

    def test_create_pin(self, get_random_user, get_rand_category):
        """
        Tests the create_pin function then, deletes the newly created pin to save DB space
        :param get_random_user:
        :param get_rand_category:
        :return:
        """

        title = f"Test pin #{randint(1, 1000)}"
        image_id = f"https://storage.googleapis.com/{BUCKET_NAME}/No_image_available.svg.png"
        assert create_pin(title=title, about=f"This is a test pin",
                          category=get_rand_category,
                          image_id=image_id, posted_by=get_random_user['username']) == {"success": True}
        new_pin = get_pin(title=title, posted_by=get_random_user['username'])
        delete_pin(pin_id=str(new_pin['pin_id']))  # clean up

    def test_get_pin_by_category(self, get_rand_category):
        """
        Tests the get_pins_by_category function using random categories from the list above
        :param get_rand_category:
        :return:
        """

        assert get_pins_by_category(categories=get_rand_category) == get_pins_by_category(categories=get_rand_category)

    def test_get_pin_by_id(self):
        """
        Tests the get_pin_by_id function, uses the get_random_pin function to pull a random pin from the DB
        :return:
        """

        pin = get_random_pin()
        assert get_pin_by_id(pin_id=str(pin['pin_id'])) == get_pin_by_id(pin_id=str(pin['pin_id']))

    def test_update_pin_title(self):
        """
        Tests the update_pin_title function, updates the title of a pin using a random int
        :return:
        """

        pin = get_random_pin()
        assert update_pin_title(pin_id=str(pin['pin_id']),
                                title=f"Updated title #{randint(1, 1000)}"
                                ) == {"success": True}

    def test_update_pin_about(self):
        """
        Tests the update_pin_about, updates the about section of a pin
        :return:
        """
        pin = get_random_pin()
        assert update_pin_about(pin_id=str(pin['pin_id']),
                                about=f"Updated about section #{randint(1, 1000)}"
                                ) == {"success": True}

    def test_update_pin_category(self, get_rand_category):
        """
        Tests for updating the category of a pin, pulls from the list of categories above
        :param get_rand_category:
        :return:
        """
        pin = get_random_pin()
        assert update_pin_category(pin_id=str(pin['pin_id']),
                                   category=get_rand_category
                                   ) == {"success": True}

    def test_delete_pin(self, get_rand_category, get_random_user):
        """
        Tests the delete_pin function. First creates a new pin and then deletes it
        :param get_rand_category:
        :param get_random_user:
        :return:
        """
        title = f"Test pin #{randint(1, 1000)}"
        image_id = f"https://storage.googleapis.com/{BUCKET_NAME}/No_image_available.svg.png"
        create_pin(title=title, about=f"This is a test pin",
                   category=get_rand_category,
                   image_id=image_id, posted_by=get_random_user['username'])
        pin = get_pin(title=title, posted_by=get_random_user['username'])
        assert delete_pin(pin_id=str(pin['pin_id'])) == {"success": True}
