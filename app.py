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

toolbar = DebugToolbarExtension(app)

connect_db(app)

CURR_USER_KEY_NAME = "curr_user"

API_BASE_URL = 'https://api.spoonacular.com/recipes'


##############################################################################
# Helper functions

@app.before_request
def add_user_to_g():
    """If we're logged in, add current user to Flask global."""

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
        

###################################################################
# About page
        
@app.route('/about')
def about_page():
    """To show about page"""

    return render_template('about.html')


####################################################################
#User routes:

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up a user and create a user profile"""

    form = SignupForm()

    if g.user:
        return redirect('/recipes')
    
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
        flash(f'Welcome, {user_obj.username}!', 'success')
        return redirect('/recipes')   
    else:
        return render_template('/users/signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
  
        user_obj = User.authenticate(username, password)

        if user_obj:
            do_login(user_obj)
            return redirect('/recipes')
        else: 
            flash('Your username or password is incorrect. Please try again.', 'danger')
            
    return render_template('/users/login.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    """Log out user"""

    do_logout()
    flash('You are logged out', 'success')
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
            flash('Your user profile has been updated!', 'success')
            return redirect('/edit_profile')
        else:
            flash('Your password is incorrect', 'danger')

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
    flash('Your profile has been deleted!', 'success')
    return redirect('/recipes')


##################################################
#Recipe Routes:

@app.route('/')
def homepage():
    """Show homepage of Recipe Finder"""

    return render_template('homepage.html')


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
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

            #Get random recipes
            if diet == 'None' and intolerances == [] and exclude_ingredients == '' and food_type == '':
                if num_of_recipes == None: 
                    resp = requests.get(f'{API_BASE_URL}/random', 
                                   params ={'apiKey': API_SECRET_KEY, 'number':10})
                else: 
                    resp = requests.get(f'{API_BASE_URL}/random', 
                                   params ={'apiKey': API_SECRET_KEY, 'number':num_of_recipes})
                
                data = resp.json()

                # Maximum API calls have been reached
                if 'code' in data:
                    flash('Please try searching for recipes tomorrow!', 'danger')
                    return redirect('/')
                
                if g.user:
                    recipe_ids =  [recipe.recipe_id for recipe in g.user.saved_recipes]   
                    return render_template('recipes/random_recipes.html', data=data, recipe_ids=recipe_ids)                   
                else:
                    return render_template('recipes/random_recipes.html', data=data)
            
            else:
                # Get filtered recipes
                resp = requests.get(f'{API_BASE_URL}/complexSearch', 
                            params = {'apiKey': API_SECRET_KEY, 'diet': diet, 'intolerances': intolerances, 
                                    'excludeIngredients': exclude_ingredients, 'query':food_type,
                                        'number': num_of_recipes})
              
                data = resp.json()
                
                # Maximum API calls have been reached
                if 'code' in data:
                    flash('Please try searching for recipes tomorrow!', 'danger')
                    return redirect('/')
                
                # No recipe results show up
                elif data['results'] == []:
                    flash('No recipes found with those selections', 'danger')
                    return redirect('/recipes')
            
            if g.user:
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
        notes = Note.query.filter(Note.user_id==g.user.id, Note.recipe_id==recipe_id).all()   #[{Note1}, {Note2}]
        users_saved_recipe_ids = [recipe.recipe_id for recipe in g.user.saved_recipes]  #[{Recipe1}, {Recipe2}]
        return render_template('recipes/recipes_info.html', form=form, data=data, recipe_id=recipe_id, notes=notes, users_saved_recipe_ids=users_saved_recipe_ids)
    else: 
        return render_template('recipes/recipes_info.html', form=form, data=data, recipe_id=recipe_id)


@app.route('/save_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def save_recipe(recipe_id):
    """To save a recipe for the user. Adds the recipe to the db"""

    if g.user:         
            users_saved_recipes = g.user.saved_recipes

            recipe_ids = [recipe.recipe_id  for recipe in users_saved_recipes]

            if recipe_id in recipe_ids:
                flash('Your recipe has been saved!', 'success')
                return redirect('/users_recipes')
            
         
            resp = requests.get(f'{API_BASE_URL}/{recipe_id}/information',
                            params={'apiKey': API_SECRET_KEY})
        
            data = resp.json()

            image = f"https://spoonacular.com/recipeImages/{recipe_id}-312x231.jpg"

            save_recipe = Saved_Recipe(user_id=g.user.id, recipe_id=recipe_id, title=data['title'], image_url=image) 
            db.session.add(save_recipe)
            db.session.commit()
            flash('Your recipe has been saved!', 'success')
            return redirect('/users_recipes')
    else:
        flash("Sign Up or Log In to save recipes", 'danger')
        return redirect(f'/recipe/{recipe_id}')


@app.route('/users_recipes')
def users_recipes():
    """To show a user's saved recipes"""

    if not g.user:
        flash('Access Unauthorized', 'danger')
        return redirect('/')

    users_recipes = g.user.saved_recipes

    recipe_ids = [recipe.recipe_id for recipe in users_recipes]
    
    if len(users_recipes) == 0:
        flash('You have no saved recipes', 'danger')
    
    return render_template('recipes/users_recipes.html', users_recipes=users_recipes, recipe_ids=recipe_ids)


@app.route('/delete_recipe/<int:recipe_id>/<int:user_id>', methods=['POST'])
def delete_saved_recipe(recipe_id, user_id):
    """To delete a user's saved recipe"""

    if not g.user or g.user.id != user_id:
        flash('Access Unauthorized', 'danger')
        return redirect('/')
    
    saved_recipes = g.user.saved_recipes

    recipe = Saved_Recipe.query.filter(Saved_Recipe.user_id==g.user.id, Saved_Recipe.recipe_id==recipe_id).first()
 
    if recipe not in saved_recipes:
        flash('Your recipe has been deleted!', 'success')
        return redirect('/users_recipes')

    db.session.delete(recipe)
    db.session.commit()
    flash('Your recipe has been deleted!', 'success')
    return redirect('/users_recipes')


###########################################################
#Note Routes:

@app.route('/save_notes/<int:recipe_id>', methods=['POST'])
def save_notes(recipe_id):
    """To save a recipe note"""

    if not g.user:
        flash('Access unauthorized', 'danger')
        return redirect('/')

    form = NoteForm()

    if form.validate_on_submit():
        
        note = form.note.data

        if note == "":
            flash('Your note is empty. Please try again.', 'danger')
            return redirect(f'/recipe/{recipe_id}')

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

    notes = Note.query.filter(Note.user_id==g.user.id, Note.recipe_id==recipe_id).all()
    
    recipe = Saved_Recipe.query.filter(Saved_Recipe.recipe_id==recipe_id, Saved_Recipe.user_id==g.user.id).first()
  
    return render_template('notes/notes.html', notes=notes, recipe_id=recipe_id, title=recipe.title, image_url=recipe.image_url)


@app.route('/delete_note/<int:note_id>/<int:recipe_id>/<int:user_id>', methods=['POST'])
def delete_note(note_id, recipe_id, user_id):
    """To delete a recipe note"""

    if not g.user or g.user.id != user_id:
        flash('Access Unauthorized', 'danger')
        return redirect('/')
    
    users_notes = g.user.notes
    
    note = Note.query.get(note_id)

    if note not in users_notes:
        flash('Your note has been deleted!', 'success')
        return redirect(f'/edit_notes/{recipe_id}')

    db.session.delete(note)
    db.session.commit()
    flash('Your note has been deleted!', 'success')
    return redirect(f'/edit_notes/{recipe_id}')






    





