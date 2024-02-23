import os
from unittest import TestCase
from models import db, User, Saved_Recipe, Note

os.environ['DATABASE_URL'] = "postgresql:///recipes_db-test"

from app import app, CURR_USER_KEY_NAME

app.config['WTF_CSRF_ENABLED'] = False

db.create_all()


class RecipeViewTestCase(TestCase):
    """Test routes and view functions for recipes"""

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
        
        resp = c.post('/recipes', data=dict)
        
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('<h5 class="recipe-list-title display-6 fw-semibold fst-italic font-style">Random Recipes:</h5>', html)


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
        
        resp = c.post('/recipes', data=dict)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h5 class="recipe-list-title font-style display-6 fw-semibold fst-italic">Filtered Recipes:</h5>', str(resp.data))
 

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
        
        resp = c.post('/recipes', data=dict, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('No recipes found with those selections', str(resp.data))

        
    def test_show_recipe_info(self):
        """Test that a user can see the information about a recipe"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        resp = c.get('/recipe/715446')

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h3 class="mt-4">Ingredients:</h3>', str(resp.data))
       

    def test_save_recipe(self):
        """Test that a user can save a recipe"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        resp = c.post('/save_recipe/715446', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h5 class="recipe-list-title display-6 fw-semibold fst-italic font-style">Saved Recipes:</h5>', str(resp.data))


    def test_not_user_save_recipe(self):
        """Test that a user cannot save a recipe if not logged in"""

        with self.client as c:
            with c.session_transaction() as session:
                session

        resp = c.post('/save_recipe/715446', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Sign Up or Log In to save recipes', str(resp.data))

    
    def test_show_users_saved_recipes(self):
        """Test that a user can view saved recipes"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        c.get('/save_recipe/715446', follow_redirects=True)

        resp = c.get('users_recipes')

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h5 class="recipe-list-title display-6 fw-semibold fst-italic font-style">Saved Recipes:</h5>', str(resp.data))
        self.assertIn('<a href="/recipe/715446" class="text-decoration-none">', str(resp.data))


    def test_delete_saved_recipe(self):
        """Test that a user can delete a saved recipe"""

        with self.client as c: 
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        c.get('/save_recipe/715446', follow_redirects=True)

        resp = c.post('/delete_recipe/715446/9999', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Your recipe has been deleted!', str(resp.data))


    def test_other_user_delete_recipe(self):
        """Test that when logged in, another user cannot delete your saved recipes"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = self.user_id

        c.get('/save_recipe/715446', follow_redirects=True)


        another_user = User.signup('anotheruser', 'another@email.com', 'another123', 'Vegan', ['Dairy'], 'peanuts')
        db.session.commit()

        another_user.id = 4444
   
        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY_NAME] = 4444
    

        resp = c.post(f'/delete_recipe/715446/{self.user_id}', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Access Unauthorized', str(resp.data))


    


        
    



