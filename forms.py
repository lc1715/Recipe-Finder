from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


diets = ['None', 'Gluten Free', 'Ketogenic', 'Vegetarian', 'Lacto-Vegetarian', 
        'Ovo-Vegetarian', 'Vegan', 'Pescatarian', 'Paleo', 'Primal',
        'Low FODMAP', 'Whole30']

intolerances = ['Dairy', 'Egg', 'Gluten', 'Grain', 'Peanut', 'Seafood',
                'Sesame', 'Shellfish', 'Soy', 'Sulfite', 'Tree Nut', 'Wheat']

meal_types = ['main course', 'side dish', 'dessert', 'appetizer', 'salad',
              'bread', 'breakfast', 'soup', 'beverage', 'sauce', 'marinade',
              'fingerfood', 'snack', 'drink']



class SignupForm(FlaskForm):
    """Form to sign up a user"""

    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    diet = SelectField('Diet (Optional)', choices = [(diet, diet) for diet in diets])
    intolerances = SelectMultipleField('Allergies/Intolerances (Optional)', choices=[(intolerance, intolerance) for intolerance in intolerances])
    exclude_ingredients = StringField('Ingredients to Exclude (Optional)')



class LoginForm(FlaskForm):
    """Form to log in a user"""

    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])



class EditProfileForm(FlaskForm):
    """Form to edit a user's profile"""

    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    email = EmailField('Email', validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Please enter your password to save your changes:', validators=[DataRequired(), Length(min=6)])
    diet = SelectField('Diet (Optional)', choices = [(diet, diet) for diet in diets])
    intolerances = SelectMultipleField('Allergies/Intolerances (Optional)', choices=[(intolerance, intolerance) for intolerance in intolerances])
    exclude_ingredients = StringField('Ingredients to Exclude (Optional)')



class RecipeForm(FlaskForm):
    """Form for a user to optionally filter out recipes"""

    diet = SelectField('Diet', choices = [(diet, diet) for diet in diets])
    intolerances = SelectMultipleField('Food Allergies/Intolerances', choices=[(intolerance, intolerance) for intolerance in intolerances])
    exclude_ingredients = StringField('Ingredients to Exclude (e.g. poppyseed, onions, etc.)')
    food_type = StringField('Type of Food (e.g. pasta, chicken, fish, etc.)')
    meal_type = SelectMultipleField('Meal Type', choices =[(meal_type, meal_type) for meal_type in meal_types])
    equipment = SelectField('Slow Cooker or Instant Pot', choices = [('None', 'None'), ('Slow Coooker', 'Slow Cooker'), ('Instant Pot', 'Instant Pot')])


class NotesForm(FlaskForm):
    """Add notes to saved recipes"""

    notes = TextAreaField('Notes')