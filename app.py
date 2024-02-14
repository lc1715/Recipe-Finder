import os
import requests

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from secret_keys import FLASK_SECRET_KEY, API_SECRET_KEY
from forms import SignupForm, LoginForm, EditProfileForm, RecipeForm, NoteForm
from models import db, connect_db, User, Saved_Recipe, Note

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///recipes_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', FLASK_SECRET_KEY)

app.app_context().push()  

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


CURR_USER_KEY_NAME = "curr_user"

API_BASE_URL = 'https://api.spoonacular.com/recipes'


##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If user is logged in, add current user as Flask global variable."""

    if CURR_USER_KEY_NAME in session:      
        g.user = User.query.get(session[CURR_USER_KEY_NAME])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY_NAME] = user.id       


def do_logout():
    """Logout user"""

    if CURR_USER_KEY_NAME in session:
        del session[CURR_USER_KEY_NAME]


@app.route('/')
def homepage():
    """Go to homepage"""

    return render_template('homepage.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up a user and create an account"""

    form = SignupForm()
    
    if form.validate_on_submit():       
        username = form.username.data
        email = form.email.data
        password = form.password.data
        diet = form.diet.data
        intolerances= form.intolerances.data
        exclude_ingredients = form.exclude_ingredients.data

        try:
            user_obj = User.signup(username, email, password, diet, intolerances, exclude_ingredients)
            db.session.commit() 
        except IntegrityError:
            flash('Username or email is already taken', 'danger')
            return render_template('/users/signup.html', form=form)
        
        do_login(user_obj)

        flash(f'Welcome, {user_obj.username}!', 'danger')

        return redirect('/recipes_form')  
    else:
        return render_template('/users/signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
  
        resp = User.authenticate(username, password)

        if resp:
            do_login(resp)
            return redirect('/recipes_form')
   
        flash('Your username or password is incorrect. Please try again', 'danger')
        
    return render_template('/users/login.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    """Log out user"""

    do_logout()
    flash('You are logged out', 'primary')
    return redirect('/')


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_user_profile():
    """Edit a user's profile"""

    if not g.user:
        flash('Access unauthorized', 'danger')
        return redirect('/')

    form = EditProfileForm()

    if request.method == 'GET' and g.user:
        form.username.data = g.user.username
        form.email.data = g.user.email
        form.diet.data = g.user.diet
        form.intolerances.data = g.user.intolerances
        form.exclude_ingredients.data = g.user.exclude_ingredients

    if form.validate_on_submit():
        # username = form.username.data
        # email = form.email.data
        # password = form.password.data
        # diet = form.diet.data
        # intolerances= form.intolerances.data        
        # exclude_ingredients = form.exclude_ingredients.data

        user_obj = User.authenticate(g.user.username, form.password.data)

        if user_obj:

            try:
                user_obj.username = form.username.data
                user_obj.email = form.email.data
                user_obj.diet = form.diet.data
                user_obj.intolerances = form.intolerances.data
                user_obj.exclude_ingredients = form.exclude_ingredients.data

                db.session.add(user_obj)  
                db.session.commit()
            except IntegrityError():
                flash('Username or email is already taken', 'danger')
                return render_template('/users/edit_profile.html', form=form)
            flash('Your user profile has been updated', 'danger')
            return redirect('/')
        else:
            flash('Your username or password is incorrect', 'danger')
    return render_template('/users/edit_profile.html', form=form)


@app.route('/delete_user', methods=['POST'])
def delete_user():
    """To delete a user"""

    if not g.user:
        flash('Access Unauthorized', 'danger')
        return redirect('/')
    
    do_logout()

    db.session.delete(g.user)
    db.session.commit()
    flash('Your account has been deleted', 'danger')
    return redirect('/recipes_form')



########################################################
#Recipe Routes:

@app.route('/recipes_form', methods=['GET', 'POST'])
def recipes_form():
    """Show recipes form. Get list of filtered recipes or random recipes"""

    form = RecipeForm()
 
    if request.method == 'GET' and g.user:

        form.diet.data = g.user.diet
        form.intolerances.data = g.user.intolerances
        form.exclude_ingredients.data = g.user.exclude_ingredients

    else:

        if form.validate_on_submit():
            
            diet = form.diet.data
            intolerances = form.intolerances.data
            exclude_ingredients = form.exclude_ingredients.data
            food_type = form.food_type.data
            num_of_recipes = form.num_of_recipes.data

            # Get random recipes:
            if diet == 'None' and intolerances == [] and exclude_ingredients == '' and food_type == '':
                resp = requests.get(f'{API_BASE_URL}/random', 
                                   params ={'apiKey': API_SECRET_KEY, 'number':9})
                
                data = resp.json()

                # Maximum API calls have been reached
                if 'code' in data:
                    flash('Please try searching for recipes tomorrow!', 'danger')
                    return redirect('/')
                
                if g.user:
                    # Get all recipe ids in user's saved recipes to change star btn color
                    recipe_ids =  [recipe.recipe_id for recipe in g.user.saved_recipes]

                    return render_template('recipes/random_recipes.html', data=data, recipe_ids=recipe_ids)                
                else:
                    return render_template('recipes/random_recipes.html', data=data)
            
            else:
                # Get filtered recipes:
                resp = requests.get(f'{API_BASE_URL}/complexSearch', 
                            params = {'apiKey': API_SECRET_KEY, 'diet': diet, 'intolerances': intolerances, 
                                    'excludeIngredients': exclude_ingredients, 'query':food_type,
                                        'number': num_of_recipes})

                data = resp.json()

                # Maximum API calls have been reached
                if 'code' in data:
                    flash('Please try searching for recipes tomorrow!', 'danger')
                    return redirect('/')
                
                elif data['results'] == []:
                    flash('No recipes found with those selections', 'danger')
                    return redirect('/recipes_form')
            
            if g.user:
                # Get all recipe ids in user's saved recipes to change star btn color
                recipe_ids =  [recipe.recipe_id for recipe in g.user.saved_recipes]
                
                return render_template('recipes/recipes_list.html', data=data, recipe_ids=recipe_ids)
            else:
                return render_template('recipes/recipes_list.html', data=data)

    return render_template('recipes/recipes_form.html', form=form)


@app.route('/recipe/<int:recipe_id>')
def get_recipe_info(recipe_id):
    """To show more information about a recipe. If the recipe has been saved by a user,
    the user can save notes about the recipe."""

    form = NoteForm()
    
    resp = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information',
                        params={'apiKey': API_SECRET_KEY})
    
    data = resp.json()

    if g.user:
        notes = Note.query.filter(Note.recipe_id==recipe_id).all()  
        users_saved_recipe_ids = [recipe.recipe_id for recipe in g.user.saved_recipes]               #[{Recipe1}, {Recipe2}]
        return render_template('recipes/recipes_info.html', form=form, data=data, recipe_id=recipe_id, notes=notes, users_saved_recipe_ids= users_saved_recipe_ids)
    else: 
        return render_template('recipes/recipes_info.html', form=form, data=data, recipe_id=recipe_id)

    
@app.route('/save_recipe/<int:recipe_id>')
def save_recipe(recipe_id):
    """To save a recipe for the user. Adds the recipe to the db"""

    if g.user:
        recipe = Saved_Recipe.query.filter(Saved_Recipe.user_id==g.user.id, Saved_Recipe.recipe_id==recipe_id).first()

        if recipe in g.user.saved_recipes:
            flash('You already saved that recipe', 'danger')
        else:
            resp = requests.get(f'{API_BASE_URL}/{recipe_id}/information',
                            params={'apiKey': API_SECRET_KEY})
        
            data = resp.json()

            image = f"https://spoonacular.com/recipeImages/{recipe_id}-312x231.jpg"

            save_recipe = Saved_Recipe(user_id=g.user.id, recipe_id=recipe_id, title=data['title'], image_url=image) 
            db.session.add(save_recipe)
            db.session.commit()
            flash('Your recipe has been saved', 'danger')
            return redirect('/users_recipes')
    else:
        flash('Sign up or log in to save recipes', 'danger')
        return redirect(f'/recipe/{recipe_id}')


@app.route('/users_recipes')
def users_recipes():
    """To show a user's saved recipes"""

    if not g.user:
        flash('Access Unauthorized', 'danger')
        return redirect('/')

    users_recipes = g.user.saved_recipes

    recipe_ids = [ recipe.recipe_id for recipe in users_recipes]
    
    if len(users_recipes) == 0:
        flash('You have no saved recipes', 'danger')
    
    return render_template('recipes/users_recipes.html', users_recipes=users_recipes, recipe_ids=recipe_ids)


@app.route('/delete_recipe/<int:recipe_id>/<int:user_id>', methods=['POST'])
def delete_saved_recipe(recipe_id, user_id):
    """To delete a user's saved recipe"""

    if not g.user or g.user.id != user_id:
        flash('Access Unauthorized', 'danger')
        return redirect('/')
    
    recipe = Saved_Recipe.query.filter(Saved_Recipe.user_id==g.user.id, Saved_Recipe.recipe_id==recipe_id).first()
 
    db.session.delete(recipe)
    db.session.commit()
    flash('Your recipe has been deleted', 'danger')
    return redirect('/users_recipes')


###########################################################
#Notes Routes:

@app.route('/save_notes/<int:recipe_id>', methods=['POST'])
def save_notes(recipe_id):
    """To save a recipe note"""

    if not g.user:
        flash('Access unauthorized', 'danger')
        return redirect('/')
    
    form = NoteForm()

    if form.validate_on_submit():
        
        note = form.note.data

        saved_recipe_obj = Saved_Recipe.query.filter(Saved_Recipe.user_id==g.user.id, Saved_Recipe.recipe_id==recipe_id).first()

        save_note = Note(saved_recipe_id=saved_recipe_obj.id, user_id=g.user.id, recipe_id=recipe_id, text=note)
  
        db.session.add(save_note)
        db.session.commit()
    
        return redirect(f'/recipe/{recipe_id}')


@app.route('/edit_notes/<int:recipe_id>')
def edit_notes(recipe_id):
    """Show all notes for a recipe and provide the option to delete a note"""

    if not g.user:
        flash('Access Unauthorized', 'danger')
        return redirect('/')

    notes = Note.query.filter(Note.recipe_id==recipe_id).all()

    return render_template('notes/notes.html', notes=notes, recipe_id=recipe_id)


@app.route('/delete_note/<int:note_id>/<int:recipe_id>/<int:user_id>', methods=['POST'])
def delete_note(note_id, recipe_id, user_id):
    """To delete a recipe note"""

    if not g.user or g.user.id != user_id:
        flash('Access Unauthorized', 'danger')
        return redirect('/')
    
    note = Note.query.get(note_id)

    db.session.delete(note)
    db.session.commit()

    return redirect(f'/edit_notes/{recipe_id}')






    











