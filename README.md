# Flask Inventory Management (FIM)

This application is built as a microservice. There are 2 microservices and a shared library package:

- IAM Service (`iam_service`)
- Inventory Service (`inventory_service`)
- FIM Shared (`fim_shared`)

# Getting Started

## Requirements

- Docker
- docker-compose

## Docker Setup

```bash
$ docker-compose -p fim build --no-cache
$ docker-compose -p fim up -d
```

## Running the Flask App Manually

If you prefer not to auto-run the flask app in the Docker container,
you can comment out `poetry run python app.py` and uncomment `tail -f /dev/null` in the .docker/entrypoint.sh file
and then connect to the service container and run the following commands from inside:

### IAM Service

```bash
$ docker exec -it iam-service /bin/bash
$ poetry run python app.py
```

### Inventory Service

```bash
$ docker exec -it inventory-service /bin/bash
$ poetry run python app.py
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

### Getting an Auth Token

1. Create a new user
2. Login with the new user
3. Copy the token received
4. Click on the Authorize button on the top right corner and enter `Token <token>` and click Authorize

### IAM Service

`http://localhost:5001/api/docs`

### Inventory Service

`http://localhost:5002/api/docs`
