# tests for comments

import pytest
from random import choice
from faker import Faker

from pintrigue_backend.database.mongodb.db_comment import create_comment,   get_random_comment, get_comment, \
    update_comment, delete_comment
from pintrigue_backend.database.mongodb.db_pin import get_random_pin
from pintrigue_backend.database.mongodb.db_user import get_all_users


fake = Faker()


@pytest.fixture
def get_random_user():
    posted_by = get_all_users()
    return choice(posted_by)


class TestCommentClass:

    def test_create_comment(self, get_random_user):
        pin = get_random_pin()
        assert create_comment(pin_id=str(pin['pin_id']),
                              posted_by=get_random_user['username'],
                              comment=fake.text()) == {"success": True}

    def test_update_comment(self):
        comment = get_random_comment()
        assert update_comment(comment_id=str(comment['comment_id']),
                              comment=f"Updated Comment - {fake.text()}"
                              ) == {"success": True}

    def test_delete_comment(self, get_random_user):
        pin = get_random_pin()
        comment = fake.text()
        create_comment(pin_id=str(pin['pin_id']),
                       posted_by=get_random_user['username'],
                       comment=comment)
        comment = get_comment(pin_id=str(pin['pin_id']), posted_by=get_random_user['username'], comment=comment)
        assert delete_comment(comment_id=str(comment['comment_id'])) == {"success": True}
