# TInventory
Inventory toolkit in order not to lose technology stuff anymore 

*Notice:* This is a kind of software specially developed for the technology working group on Katharineum zu Lübeck. It's OK, of course, to use it for other purposes. 

# Installation instructions
## Development system
1. Create virtual Python 3 environment in project directory
`$ python3 -m venv env`
2. Activate virtual env 
`$ source env/bin/activate`
2. Install needed pip libraries by `(env) $ pip install -r requirements.txt`
3. Do migrations
`(env) $ python manage.py makemigrations && python manage.py migrate`
5. Create first user
`(env) $ python manage.py createsuperuser`
4. Run development server
`(env) $ python manage.py runserver`

## Production system using Docker
1. Install Docker
2. Install docker-compose
3. Go to project directory
4. Customize settings from `docker-compose.yml` via creating `docker-compose.override.yml`
5. Run docker container 
    - `$ docker-compose up` (foreground)
    - `$ docker-compose up -d` (background)

More information about Docker could be found on https://docker.com
