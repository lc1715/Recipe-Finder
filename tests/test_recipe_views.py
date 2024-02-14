# To run tests: FLASK_ENV=production python3 -m unittest tests/test_recipe_views.py

import os

from unittest import TestCase
from models import db, connect_db, User, Saved_Recipe, Note

os.environ['DATABASE_URL'] = "postgresql:///recipes_db-test"

from app import app, CURR_USER_KEY_NAME, API_BASE_URL

app.config['WTF_CSRF_ENABLED'] = False

db.create_all()


class RecipeViewTestCase(TestCase):
    """Test routes and view functions for users"""

    def setUp(self):
        """Create test client, delete and create tables, and add sample data"""

        self.client = app.test_client()

        db.drop_all()
        db.create_all()

        user = User.signup('testuser', 'test@email.com', 'testing123', 'Vegan', ['Dairy', 'Gluten'], 'peanuts')

        user.id = 2222
        
        db.session.commit()

        self.user_id = user.id
        self.user = user

    def tearDown(self):
        """Clear up fouled transactions"""

        db.session.rollback()


    def test_get_random_recipes(self):
        """Test that a user can receive random recipes"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id


        dict = {'diet':'None', 
             'intolerances': [],
             'exclude_ingredients': '',
             'food_type': ''}
        
        resp = c.post('/recipes_form', data=dict)
        
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('<h5 class="display-5 text-center">Random Recipes</h5>', html)


    def test_get_filtered_recipes(self):
        """Test that a user can receive filtered recipes"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id


        dict =  {'diet': 'Vegan',
                'intolerances': ['Dairy', 'Grain'],
                'exclude_ingredients': 'beans, onion',
                'food_type': 'broccoli',
                'num_of_recipes': 1}
        
        resp = c.post('/recipes_form', data=dict)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h5 class="display-5 text-center">Recipes</h5>', str(resp.data))


    def test_invalid_input_recipe_search(self):
        """Test an invalid query in recipe form"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id


        dict =  {'diet': 'None',
                'intolerances': [],
                'exclude_ingredients': 'asdfasef',
                'food_type': '',
                'num_of_recipes': 1}
        
        resp = c.post('/recipes_form', data=dict, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('No recipes found with those selections', str(resp.data))

        
    def test_show_recipe_info(self):
        """Test that a user can see the information about a recipe"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        resp = c.get('/recipe/715446')

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h6>Ingredients:</h6>', str(resp.data))
       

    def test_save_recipe(self):
        """Test that a user can save a recipe"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        resp = c.post('/save_recipe/715446', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h5 class="display-5 text-center">Recipes</h5>', str(resp.data))


    def test_not_user_save_recipe(self):
        """Test that a user cannot save a recipe if not logged in"""

        with self.client as c:
            with c.session_transaction() as session:
                session

        resp = c.post('/save_recipe/715446', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Sign up or log in to save recipes', str(resp.data))

    
    def test_show_users_saved_recipes(self):
        """Test that a user can see saved recipes"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        c.get('/save_recipe/715446', follow_redirects=True)

        resp = c.get('users_recipes')

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h5 class="display-5 text-center">Recipes</h5>', str(resp.data))
        self.assertIn('<a href="/recipe/715446">', str(resp.data))


    def test_delete_saved_recipe(self):
        """Test that a user can delete a saved recipe"""

        with self.client as c: 
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        c.get('/save_recipe/715446', follow_redirects=True)

        resp = c.post('/delete_recipe/715446', data={}, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Your recipe has been deleted', str(resp.data))


    


        
    



