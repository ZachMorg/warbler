"""Message model tests"""


import os
from unittest import TestCase

from models import db, User, Message, Follows


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app


db.create_all()

class MessageModelTestCase(TestCase):
    
    def setUp(self):

        User.query.delete()
        Message.query.delete()

        self.uid = 989898
        u = User.signup("test", "anemail@email.email", "password123", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)
        
        self.client = app.test_client()        

    def test_message_model(self): 
        """Does the Message model work?"""


        m = Message(
            text="Test",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m, Message.query.get(m.id))