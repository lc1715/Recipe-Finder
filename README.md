# Recipe Finder

This web application was designed to help users who are on a dietary restriction due to food allergies or intolerances to easily search for recipes. Users who do not have any dietary restrictions can also use this web application to search through thousands of recipes.     

Live App: [Recipe Finder](https://recipe-finder-kigw.onrender.com) 

![homepage recipe finder](https://github.com/user-attachments/assets/c4b28e20-5e83-4c4b-89e6-86597674951d)
<img width="40%" alt="recipe filter form" src="https://github.com/user-attachments/assets/dbffdbfb-10f2-4c11-b12a-a76b7f177708" />
<img width="50%" alt="filtered recipes" src="https://github.com/user-attachments/assets/f4acb648-4390-4433-b268-62f848be3a85" />
<img width="1446" height="800" alt="random recipes" src="https://github.com/user-attachments/assets/8afe0b5c-4900-48d1-8512-9534b6db944c" />
<img width="1401" height="867" alt="saved recipes" src="https://github.com/user-attachments/assets/2fcc5e9f-890b-439f-a60f-ab26e904794f" />
<img width="1351" height="760" alt="recipe details" src="https://github.com/user-attachments/assets/3bf3b26d-6ade-4a09-acf0-7ff853af8845" />

# Features

**Users without an account can:**
	
* Filter and search for recipes based on their diet, food allergies/intolerances, ingredients to exclude, food type, meal type, and number of recipes to return. All  of the filter selections are optional. If none of the choices are selected, then a surprise list of random recipes will be returned. 

* Sign up and create an account. See what users with an account can do below!

**Users with an account can:**

* Do everything that anonymous users can

* Save their filter selections based on their dietary restrictions. (This will prevent users from having to re-enter their dietary restrictions each time they search for recipes.)

* Save their favorite recipes and add their own personal notes to those recipes. (e.g. If recipe ingredients were modified or adjusted, users can take notes to remind themselves the next time they make that meal.)

* Update their user profile in case their personal information or dietary restrictions have changed. They can also delete their own profile in case they want to terminate their account.

# Tech Stack
* Database: PostgreSQL
* Backend: Python, Flask, SQLAlchemy, WTForms
* Frontend: Jinja, CSS, Bootstrap, jQuery
* API: [Spoonacular](https://spoonacular.com/food-api/docs) 

# Setup
To run Recipe Finder on your local computer:

1. Clone the repo into a local directory
```
https://github.com/lc1715/Recipe-Finder.git
``` 
2. Create a virtual environment
```
python3 -m venv venv
```
3. Activate the virtual environment
```
source venv/bin/activate
```
4. Install the dependencies from the requirements.txt file
```
pip3 install -r requirements.txt
```
5. Run application
```
flask run
```
* Be sure to replace the environmental variables API_SECRET_KEY and FLASK_SECRET_KEY with your own. You can import them from a separate file. Also, you can create the database in PostgreSQL with "createdb recipes_db".

# Note
* The Spoonacular API only allows up to 150 call requests  per day for the free tier. If you don't receive any results after putting in a valid search request for recipes, Recipe Finder may have exceeded the maximum number of API calls it can make. If that's the case, please wait until the next day to search for recipes.
