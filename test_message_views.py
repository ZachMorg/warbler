"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})
            print(resp)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_delete_message(self):
        """Can user delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Delete me!"})
            print(resp)

            message = Message.query.one()
            resp = c.post(f"/messages/{message.id}/delete")
            print(resp)

            message_list = Message.query.all()
            self.assertEqual(len(message_list), 0)


    def test_log_out_add(self):
        """Is a logged out user prohibited from adding a message?"""

        with self.client as c:

            resp = c.get("/messages/new")
            print(resp)

            self.assertEqual(resp.status_code, 302)


    def test_log_out_delete(self):
        """Is a logged out user prohibited from deleting a message?"""

        m = Message(
            id=99999,
            text="Don't delete me!",
            user_id=self.testuser.id
        )
        db.session.add(m)
        db.session.commit()

        with self.client as c:

            resp = c.post(f"/messages/{Message.query.one().id}/delete")

            self.assertIn('<a href="/">/</a>', str(resp.data))


    def test_add_other_user(self):
        """Can a user add a message under a different user id?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Don't add me!", "user_id": 987654})

            print(Message.query.one().user_id)

            self.assertNotIn('987654', str(Message.query.one().user_id))