# myFoodBook
## Instructions
1. if you do not have python installed, download and install for your computer make sure to add python to PATH im using version 3.7 but newer versions should work fine
2. After python is installed you need to install dependencies requirements. You can do that with this command in cmd or terminal\
``pip install django django-crispy-forms django-taggit django-autocomplete-light Pillow``
or
``pip install -r requirements.txt``
3. Now clone or download the source code from github
4. Navigate to the folder in cmd or terminal. I open the folder in VS Studio code to make it easy but you can do in regualar terminal by using cd command. 
5. once your in the project folder type this command\
``python manage.py runserver``
6. If everything worked correctly you should be able to open a web browser and navigate to [http://localhost:8000](http://localhost:8000) where the web app should display

The main app directory is in the foodBookApp it has models.py for database, views.py for different views, urls.py for url patterns, in the templates folder there are component templates for each page, the templates inherit from base.html which helps from having to reuse same code. 

Now you can log in and make posts, and add friends. Somethings we still need to work on is the social buttons like comment and share. Also need to implement messages and search function. If anyone needs any help let me know. 

## Contributing 
Reference for github fork and pull request workflow
https://github.com/susam/gitpr

Gist: Fork a personal copy of repository, (recommended) work on self/feature branch, pull request diffs to main repository (forked-from).  Update personal forked repository with main repository changes by pulling to main.

## Notes
- If db.sqlite3 still tracked by git after gitignore entry update, ``git update-index --skip-worktree db.sqlite3`` in root directory to untrack (unstage if staged)