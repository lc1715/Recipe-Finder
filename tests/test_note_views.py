# To run tests: FLASK_ENV=production python3 -m unittest tests/test_note_views.py

import os

from unittest import TestCase
from models import db, connect_db, User, Saved_Recipe, Note


os.environ['DATABASE_URL'] = "postgresql:///recipes_db-test"

from app import app, CURR_USER_KEY_NAME

app.config['WTF_CSRF_ENABLED'] = False

db.create_all()


class NoteViewTestCase(TestCase):
    """Test routes and view functions for notes"""

    def setUp(self):
        """Create test client, empty tables, and add sample data"""
        
        self.client = app.test_client()

        db.drop_all()
        db.create_all()

        #Add a user
        user = User.signup('testuser','test@email.com', 'testing123', 'Vegan', ['Dairy'], 'peanuts') 
        db.session.commit()

        user.id = 9999

        self.user_id = user.id
        self.user = user

        #Add the user's saved recipe
        saved_recipe = Saved_Recipe(id=1, recipe_id=715446, user_id=self.user_id, title='', image_url='')
        db.session.add(saved_recipe)
        db.session.commit()

        self.recipe_id = saved_recipe.recipe_id
        self.saved_recipe = saved_recipe

    def tearDown(self):
        """Clear up fouled transactions"""

        db.session.rollback()
        

    def test_save_note(self):
        """Test that a user can save a recipe note"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        resp = c.post(f'/save_notes/{self.recipe_id}', data={'note': 'Used 1 cup of sugar instead of 2 cups of sugar and it was sweet enough'},
                      follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Used 1 cup of sugar instead of 2 cups of sugar and it was sweet enough', str(resp.data))


    def test_delete_note(self):
        """Test that a user can delete a note"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        c.post(f'/save_notes/{self.recipe_id}', data={'note': 'Used 1 cup of sugar instead of 2 cups of sugar and it was sweet enough'},
                      follow_redirects=True)

        resp = c.post('/delete_note/1/715446/9999', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h3>Delete Recipe Notes</h3>', str(resp.data))


    def test_other_user_delete_note(self):
        """Test that when you're logged in, another user cannot delete your note"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        c.post(f'/save_notes/{self.recipe_id}', data={'note': 'Used 1 cup of sugar instead of 2 cups of sugar and it was sweet enough'},
                      follow_redirects=True)


        another_user = User.signup('anotheruser', 'another@email.com', 'another123', 'Vegan', ['Dairy'], 'peanuts')
        db.session.commit()

        another_user.id = 2222
   
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = 2222
    

        resp = c.post(f'/delete_note/1/715446/{self.user_id}', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Access Unauthorized', str(resp.data))





        