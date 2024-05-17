# Library API Service

This project is a Django REST API for managing a borrowing system for library. It includes functionality for managing books, users, and borrowings. It also features JWT authentication, custom permissions, and integration with the Telegram API for notifications.

## Installing using GitHub

``` 
git clone https://github.com/pnakongit/library-service.git
cd library-service/
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
cp .env.sample .env # Edit .env file with your configuration
python manage.py migrate
python manage.py runserver
``` 

## Getting access

- create user via /api/v1/accounts/
- get access token via /api/v1/accounts/token/ . Change the default Authorization header to Authorize for JWT authentication.


## Documentation

- view documentation vai /api/v1/docs/swagger/

## Features

- CRUD functionality for Books
- CRU functionality for Users
- Borrowing management with detailed book info
- JWT token authentication
- Custom header for JWT authentication
- Role-based access control
- Real-time notifications via Telegram
