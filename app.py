import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from secret_keys import SECRET_KEY
from forms import SignupForm, LoginForm, EditProfileForm, RecipeForm
from models import db, connect_db, User, Saved_Recipe

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///recipes_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get(SECRET_KEY)

app.app_context().push()  

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()



