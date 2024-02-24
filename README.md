# Recipe Finder

This web application was designed to help users who are on a dietary restriction due to food allergies or intolerances to easily search for recipes. Users who do not have any dietary restrictions can also use this web application to search through thousands of recipes.     

Live App: [Recipe Finder](https://recipe-finder-kigw.onrender.com) 

## Features

**Users without an account can:**
	
* Filter and search for recipes based on their diet, food allergies/intolerances, ingredients to exclude, food type, meal type, and number of recipes to return. All  of the filter selections are optional. If none of the choices are selected, then a surprise list of random recipes will be returned. 

* Sign up and create an account. See what users with an account can do below!

**Users with an account can:**

* Do everything that anonymous users can

* Save their filter selections based on their dietary restrictions. (This will prevent users from having to re-enter their dietary restrictions each time they search for recipes.)

* Save their favorite recipes and add their own personal notes to those recipes. (e.g. If recipe ingredients were modified or adjusted, users can take notes to remind themselves the next time they make that meal.)

* Update their user profile in case their personal information or dietary restrictions have changed. They can also delete their own profile in case they want to terminate their account.

## Tech Stack
* API: [Spoonacular](https://spoonacular.com/food-api/docs) 
* Frontend: HTML, CSS, Bootstrap, Javascript
* Backend: Python, Flask, SQLAlchemy, WTForms, PostgreSQL 

## Setup
To run Recipe Finder on your local computer:

1. Clone the repo into a local directory 
2. Create and activate a virtual environment in the local directory
3. Install the dependencies from the requirements.txt file
4. Start the application with "flask run"

* Be sure to replace the API_SECRET_KEY and FLASK_SECRET_KEY with your own. You can import them from a separate file. Also, you can create the database in PostgreSQL with "createdb recipes_db".

## Note
* The Spoonacular API only allows up to 150 call requests  per day for the free tier. If you don't receive any results after putting in a valid search request for recipes, Recipe Finder may have exceeded the maximum number of API calls it can make. If that's the case, please wait until the next day to search for recipes.





















