# coinmarket-api-django


## Crypto API

API thats search the description, slug and name by the Symbol and store in a postgresql database. Uses redi cache for *GET* actions


### Configure the .env file using the .env.sample content as example with your data

## To run:

Execute to create an enviroment
```python
python -m venv dev_env
```

Execute to install all dependencies 
```python
pip install requirements.txt
```

Execute to start the containers for the postgresql db and redis db
```
docker-compose up
```

Execute to run the django server
```
python manage.py runserver
```