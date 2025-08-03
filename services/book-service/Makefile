run:
	python3 manage.py runserver

# 1) change models in .\books\models.py

# 2) create migrations for those changes
makemigrations:
	python3 manage.py makemigrations books

# (*) 3) just print sql tables basing on migration number  
sqlmigrate:
	python3 manage.py sqlmigrate books 0001 

# 4) apply those changes (from 2)) to the database
migrate:
	python3 manage.py migrate

# the reaason that there are separate commands to make and apply migrations is because you'll commit migrations to your version control system and ship them with your app;

createsuperuser:
	python3 manage.py createsuperuser

# # delete the SQLite database
# rmsql:
# 	rm db.sqlite3

import_books:
	python3 manage.py import_books