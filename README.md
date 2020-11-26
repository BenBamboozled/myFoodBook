# myFoodBook

## Instructions

1. If you do not have Python installed, download and install for your computer make sure to add python to PATH, Python 3.7 and newer versions should work fine.
2. Now open the project directory provided, with command prompt or terminal using the cd command. Once in the project directory you need to install needed dependencies, with one of the two commands below:
   `pip install -r requirements.txt`
   or
   `pip install django django-crispy-forms django-taggit django-autocomplete-light Pillow PyMySQL django-storages google-cloud-storage`
3. If everything is installed correctly, from inside the main project directory in cmd you can run this command:
   `python manage.py runserver`
4. If everything worked correctly you should be able to open a web browser and navigate to [http://localhost:8000](http://localhost:8000) where the web app should display.
5. To end the session just hit ctrl-C in your cmd and the server will stop.

The main app directory is in the foodBookApp it has models.py for database, views.py for different views, urls.py for url patterns, in the templates folder there are component templates for each page, the templates inherit from base.html which helps from having to reuse same code.

Now you can log in and make posts, and add friends. Somethings we still need to work on is the social buttons like comment and share. Also need to implement messages and search function. If anyone needs any help let me know.

## Contributing

Reference for github fork and pull request workflow
https://github.com/susam/gitpr

Gist: Fork a personal copy of repository, (recommended) work on self/feature branch, pull request diffs to main repository (forked-from). Update personal forked repository with main repository changes by pulling to main.

## Notes

- If db.sqlite3 still tracked by git after gitignore entry update, `git update-index --skip-worktree db.sqlite3` in root directory to untrack (unstage if staged)

## Deployment to Google Cloud

- Everything is deployed from this git at [https://myfoodbook-296719.uc.r.appspot.com/](https://myfoodbook-296719.uc.r.appspot.com/)
- settings.py has boolean flag DEPLOY when set to true it uses the cloud database else it uses the sqlite development database. By default it will use dev database.
- You will need two files that are not included in this repo because of sensitive info. You will need /etc/config.json and credentials.json please cointact me and I will give team member these files if needed. They will be included with the folder I turn in for the project.
- Hosted on the Google Cloud Platform for security, performance, scalabilitly
- Uses a cloud mysql database also provided by the Google Cloud Platform
- Any bugs or fixes can be pulled here and I will update to the deployment platform.
