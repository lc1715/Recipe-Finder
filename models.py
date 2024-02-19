from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connects the database to Flask app when called."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """To create a user in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    diet = db.Column(db.Text, default=None)
    intolerances = db.Column(db.Text, default=None)
    exclude_ingredients = db.Column(db.Text, default=None)
    saved_recipes = db.relationship('Saved_Recipe', backref='user', cascade="all, delete-orphan")
    notes = db.relationship('Note', backref='user', cascade="all, delete-orphan")


    def __repr__(self):
        return f"<user_obj: id={self.id}, username={self.username}, email={self.email}>"
    

    @classmethod
    def signup(cls, username, email, password, diet, intolerances, exclude_ingredients):
        """To sign up a user, hash the password, and return the user object."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            diet = diet,
            intolerances = intolerances,
            exclude_ingredients=exclude_ingredients
        )
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find a user with the correct `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    

class Saved_Recipe(db.Model):
    """User's saved recipes""" 

    __tablename__ = 'saved_recipes'

    __table_args__ = (db.UniqueConstraint('recipe_id', 'user_id'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    title = db.Column(db.Text)
    image_url = db.Column(db.Text)
    recipe_notes = db.relationship('Note', backref='recipe', cascade="all, delete-orphan")


class Note(db.Model):
    """User's notes for a recipe"""

    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saved_recipe_id = db.Column(db.Integer, db.ForeignKey('saved_recipes.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    recipe_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

   

    