# Library API
This is a REST api to manage a library. The core functionality is to enable registered users to reserve books. There also is 'the staff' layer which enables to manage users and books.

## Relational model.
![alt text](https://github.com/Suijn/Library/blob/master/diagram_erd.PNG?raw=true)

## Functionality.
##### User 
After successfully registering an account and logging in an user can:
- search for books
- reserve up to 5 books (user can reserve a book for 30 days)
- change his email address and password.
- view his own reservations and deadlines until which he must return books.
- prolong a book reservation (only once, for a duration of 30 days.)
##### Admin
An admin can:
- view all users, view details about a particular user, delete an user, change user email address.
- add a a new book, update, delete a book, admin can also additionaly search for books by book id.
- reserve a book for a user, cancel book reservation

## Tech stack
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Marshmallow
- Pytest

### The app is currently in development

