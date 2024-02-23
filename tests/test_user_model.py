import os
from unittest import TestCase

from models import db, User, Saved_Recipe, Note
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///recipes_db-test"

from app import app

db.create_all()    


class UserModelTestCase(TestCase):
    """Test User Model functionality"""

    def setUp(self):      
        """Empty tables and create sample data"""

        User.query.delete()
        Saved_Recipe.query.delete()
        Note.query.delete()       

        user = User(username='testuser', email='test@email.com', password='testuser123')  
        user.id = 9999

        db.session.add(user)
        db.session.commit()

        self.user_id = user.id 
        self.user = user        

    def tearDown(self):
        """Clear up any fouled transactions in session"""

        res = super().tearDown()
        db.session.rollback()
        return res
    

    def test_user_model(self):
        """Test user creation"""

        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@email.com')
        self.assertEqual(self.user.password, 'testuser123')
        self.assertEqual(len(self.user.saved_recipes), 0)
        self.assertEqual(len(self.user.notes), 0)


    def test_repr_method(self):
        """Test __repr__ method"""

        resp = User.__repr__(self.user)

        self.assertEqual(resp, '<user_obj: id=9999, username=testuser, email=test@email.com>')


    def test_signup_method(self):
        """Test the signup method"""

        user1 = User.signup('test1', 'test1@email.com', 'testing123', 'vegan', ['Dairy', 'Gluten'], None)

        self.assertNotEqual(user1.password, 'testing123')
        self.assertTrue(user1.password.startswith('$2b$'))
        self.assertEqual(user1.username, 'test1')
        self.assertEqual(user1.diet, 'vegan')
        self.assertEqual(user1.intolerances, ['Dairy', 'Gluten'])


    def test_duplicate_user_creation(self):
        """Test signup method with the same username or email as another user"""

        User.signup('test1', 'test1@email.com', 'testing123', 'vegan', ['Dairy', 'Gluten'], 'peanut')

        with self.assertRaises(IntegrityError) as context:
            User.signup('test1', 
                        'test1@email.com', 
                        'testing123', 
                        'vegan', 
                        ['Dairy', 'Gluten'], 
                        'peanut')
            db.session.commit()


    def test_authenticate_method(self):
        """Test authenticate method"""

        user1 = User.signup('test1', 'test1@email.com', 'testing123', None, None, None)

        resp = User.authenticate(user1.username, 'testing123')

        self.assertNotEqual('testing123', user1.password)
        self.assertTrue(user1.password.startswith('$2b$'))
        self.assertNotEqual(resp, False)
        self.assertEqual(resp.username, 'test1')


    def test_authenticate_invalid_username(self):
        """Test when a user provides an incorrect username"""

        user1 = User.signup('test1', 'test1@email.com', 'testing123', None, None, None)

        resp = User.authenticate('wrong_username', 'testing123')

        self.assertEqual(resp, False)
        self.assertNotEqual(user1.username, 'wrong_username')
        

    def test_authenticate_invalid_password(self):
        """Test when a user provides an incorrect password"""

        user1 = User.signup('test1', 'test1@email.com', 'testing123', None, None, None)

        resp = User.authenticate(user1.username, 'wrong_password')

        self.assertEqual(resp, False)
        self.assertNotEqual(user1.password, 'wrong_password')






        




