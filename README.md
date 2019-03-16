# tinventory
Inventory toolkit in order not to lose things anymore

# Installation instructions
1. Create virtual Python 3 environment in project directory
`$ python3 -m venv env`
2. Activate virtual env 
`$ source env/bin/activate`
2. Install needed pip libraries by `(env) $ pip install …`
```
Django
django-bootstrap-form
django-cors-headers
django-oauth-toolkit
djangorestframework
oauthlib
requests
```
3. Do migrations
`(env) $ python manage.py makemigrations && python manage.py migrate`
5. Create first user
`(env) $ python manage.py createsuperuser`
4. Run development server
`(env) $ python manage.py runserver`
