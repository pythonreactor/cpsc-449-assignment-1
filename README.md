# Flask Inventory Management (FIM)

This application is built as a microservice. There are 2 microservices and a shared library package:

- IAM Service (`iam_service`)
- Inventory Service (`inventory_service`)
- FIM Shared (`fim_shared`)

## Auxiliary Services

This application utilizes the following auxiliary sources that are part of the project:

- MongoDB
- Redis
- Redis RQ
- Elasticsearch
- NGINX

# Getting Started

## Requirements

- Docker >= v26.0.0
- docker-compose >= v2.26.1

## Docker Setup

```bash
$ cd .docker/
$ docker-compose -p fim build --no-cache
$ docker-compose -p fim up -d
```

## Running the Flask App Manually

If you prefer not to auto-run the flask app in the Docker container,
you can comment out `poetry run python app.py` and uncomment `tail -f /dev/null` in the entrypoint.sh files
and then connect to the service container and run the following commands from inside:

### IAM Service

```bash
$ docker exec -it iam-service-1 /bin/bash
$ poetry run python app.py
```

### Inventory Service

```bash
$ docker exec -it inventory-service-1 /bin/bash
$ poetry run python app.py
```

# Loadbalancing with NGINX

If you'd like to utilize the NGINX loadbalancing, you can scale your docker containers to see it in action:

```bash
$ cd .docker/
$ docker-compose -p fim build --no-cache
$ docker-compose -p fim up --scale iam-service=2 --scale inventory-service=2
```

# Adding Dependencies with Poetry

`poetry add <package-name>`

# Accessing Swagger

Each microservice has a Swagger endpoint which can be reached using `localhost:8080/api/docs/<service_name>`

### IAM Service

`http://localhost:8080/api/docs/iam`

### Inventory Service

`http://localhost:8080/api/docs/inventory`

### Getting an Auth Token

1. Create a new user
2. Login with the new user
3. Copy the token received
4. Click on the Authorize button on the top right corner and enter `Token <token>` and click Authorize

This will allow you to hit protected endpoints that require token authentication.

# Accessing the RQ Dashboard

Inventory is currently the only service with an RQ worker. The dashboard can be accessed by going to `http://localhost:8080/rq/inventory`.

# Accessing an the Elasticsearch Index in the browser

Inventory is the only service currently utilizing Elasticsearch but the top-level index can be reached by going to `http://localhost:9200/inventory/_search?pretty`.

# Running a Shell in the Docker Container

There is a script, `ipython_setup.py` that will run for you to prepare your python shell within the context of
the Flask app. It is important to run your shell from within the service docker container using:

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

## Querying Elasticsearch

If an object has an `es_query` property, it can be used for querying Elasticsearch documents.

```python
from inventory.models import Inventory

# This will return an ElasticsearchQuerySet object that can be iterated over
items = Inventory.es_query.all()
# This will return the first document in the ElasticsearchQuerySet
item = items.first()
```
