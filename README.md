# Getting Started

## Requirements

- Docker
- docker-compose

## Docker Setup

```bash
$ docker-compose build --no-cache
$ docker-compose up -d
```

## Running the Flask App Manually

If you prefer not to auto-run the flask app in the Docker container,
you can swap `command: poetry run python app.py` with `command: tail -f /dev/null` in the docker-compose.yml file
and then run the following commands from inside the built app container:

```bash
$ docker exec -it fim-app /bin/zsh
$ flask-run
```

## Running a Shell in the Docker Container

There is a script, `ipython_setup.py` that will run for you to prepare your python shell within the context of
the Flask app. It is important to run your shell using:

`poetry run ipython`

## Querying the Database

Each object has a `query` attribute tied to it for querying and handling MongoDB documents.

```python
from inventory.models import Inventory

# This will return a QuerySet object that can be iterated over
items = Inventory.query.all()
# This will return the first document in the QuerySet
item = items.first()
```

## Adding Dependencies with Poetry

`poetry add <package-name>`

## Accessing Swagger

`http://localhost:5001/api/docs`

1. Create a new user
2. Login with the new user
3. Copy the token received
4. Click on the Authorize button on the top right corner and enter `Token <token>` and click Authorize
