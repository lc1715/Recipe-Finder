import os
from unittest import TestCase

from models import db, User, Saved_Recipe, Note

os.environ['DATABASE_URL'] = "postgresql:///recipes_db-test"

from app import app, CURR_USER_KEY_NAME

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test routes and view functions for users"""

    def setUp(self):
        """Create test client, empty tables, and add sample data"""

        self.client = app.test_client()

        User.query.delete()
        Saved_Recipe.query.delete()
        Note.query.delete()

        user = User.signup('testuser', 'test@email.com', 'testing123', 'Vegan', ['Dairy', 'Gluten'], 'peanuts')

        user.id = 9999
        
        db.session.commit()

        self.user_id = user.id
        self.user = user           

    def tearDown(self):
        """Clear up any fouled transactions"""

        db.session.rollback()
        

    def test_signup_show_recipe_form(self):
        """Test that a user can sign up and view the recipe form"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        resp = c.post('/signup', data={'username':'testuser1', 'email':'test1@email.com', 'password':'testing456', 'diet':'Vegan', 'intolerances':['Dairy'], 'exclude_ingredients':'peanuts'}, 
                      follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h1 class="mb-4 mt-3 text-center">Recipe Filter</h1>', str(resp.data))


    def test_login_show_recipe_form(self):
        """Test that a user can log in and view the recipe form"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY_NAME] = self.user_id

        resp = c.post('/login', data={'username': 'testuser', 'password': 'testing123' })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, '/recipes')

        resp = c.post('/login', data={'username': 'testuser', 'password': 'testing123'}, 
                      follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('<h1 class="mb-4 mt-3 text-center">Recipe Filter</h1>', html)


    def test_edit_profile(self):
        """Test that a user can edit a profile"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY_NAME] = self.user_id

        resp = c.post('/edit_profile', data={
            'username': 'testuser',
            'email': 'test@email.com',  
            'diet': 'Vegan', 
            'intolerances': ['Dairy', 'Gluten'], 
            'exclude_ingredients': 'radish',
            'password': 'testing123'}, 
            follow_redirects=True)
      
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('Your user profile has been updated!', html)
        self.assertIn('<h1 class="mb-4 mt-3 text-center">User Profile</h1>', str(resp.data))
    

    def test_delete_user_profile(self):
        """Test that a user profile can be deleted"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY_NAME] = self.user_id

        resp = c.post('/delete_user', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Your profile has been deleted!', str(resp.data))
        html = resp.get_data(as_text=True)
        self.assertIn('<h1 class="mb-4 mt-3 text-center">Recipe Filter</h1>', html)







