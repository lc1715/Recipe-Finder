import os
import requests

from flask import Flask, render_template, flash, redirect, session, g, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from secret_keys import FLASK_SECRET_KEY, API_SECRET_KEY
from forms import SignupForm, LoginForm, EditProfileForm, RecipeForm
from models import db, connect_db, User, Saved_Recipe

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


@app.route('/')
def homepage():

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
        flash('Your account has been created.')
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
        # print('***********************', resp)

        if resp:
            do_login(resp)

            return redirect('/recipes_form')
    else:   
        flash('Your username or password is incorrect. Please try again')
        return render_template('/users/login.html', form=form)


@app.route('/logout')
def logout():
    """Log out user"""

    do_logout()
    flash('You are logged out', 'primary')
    return redirect('/')


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_user_profile():
    """Edit a user's profile"""

    form = EditProfileForm(obj=g.user)
    # raise 

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        diet = form.diet.data
        intolerances= form.intolerances.data        
        exclude_ingredients = form.exclude_ingredients.data

        user_obj = User.authenticate(username, password)

        if user_obj:
            try:
                user_obj.username = username
                user_obj.email = email
                user_obj.diet = diet
                user_obj.intolerance = intolerances
                user_obj.exclude_ingredients = exclude_ingredients
                db.session.add(user_obj)  
                db.session.commit()
            except IntegrityError():
                flash('Username or email is already taken', 'danger')
                return render_template('/users/edit_profile.html', form=form)
            flash('Your user profile has been updated')
            return redirect('/')
         
    return render_template('/users/edit_profile.html', form=form)



##################################################
#Recipe Routes:

@app.route('/recipes_form', methods=['GET', 'POST'])
def recipes_form():
    """Show recipes form, filter recipes, and get list of recipes"""

    ###GET request###########
    form = RecipeForm(obj=g.user)

    ###POST request##############
    if form.validate_on_submit():
        diet = form.diet.data
        intolerances = form.intolerances.data
        exclude_ingredients = form.exclude_ingredients.data
        food_type = form.food_type.data
        meal_type = form.meal_type.data
        equipment = form.equipment.data

        resp = requests.get(f'{API_BASE_URL}/complexSearch', 
                        params = {'apiKey': API_SECRET_KEY, 'diet': diet, 'intolerances': intolerances, 
                                  'excludeIngredients': exclude_ingredients, 'query':food_type,
                                    'type': meal_type, 'equipment': equipment})
        
        data = resp.json()
        return render_template('recipes/recipes_list.html', data=data)

    return render_template('recipes/recipes_form.html', form=form)


@app.route('/recipe/<int:recipe_id>')
def get_recipe_info(recipe_id):
    
    resp = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information',
                        params={'apiKey': API_SECRET_KEY})
    
    data = resp.json()

    return render_template('recipes/recipes_info.html', data=data)





    

