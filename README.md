# Library API
This is a REST api to manage a library. The core functionality is to enable registered users to reserve books. The app also provides an admin layer, which enables admins to manage users, books and reservations.

## Relational model
![alt text](https://github.com/Suijn/Library/blob/master/diagram_erd.PNG?raw=true)

## Functionality
##### User 
After successfully registering an account and logging in users can:
- search for books by book title and author.
- reserve up to 5 books (user can reserve a book for 30 days)
- change email address and password.
- view their reservations and deadlines until which books must be returned.
- prolong book reservations (each book reservation can be prolonged only once, for a duration of 30 days)
##### Admin
admins can:
- view all users, user details, delete a user, change user email address.
- add a new book, update, delete a book, admins can also additionaly search for books by book id.
- reserve a book for a user, cancel book reservation
- search for reservations by status, books and users.

## Tech stack
- Flask
- SQLAlchemy
- Marshmallow
- Pytest

## Additional information.
- User authentication is implemented using JWT (access token: 15 min., refresh token: 30 days.)
- User password is hashed using Bcrypt.
- Permissions are handled using roles: **Admin, User**. User is the default role, admins are currently created using a CLI command (source: [link](https://github.com/Suijn/Library/tree/master/bookstore/commands.py))

