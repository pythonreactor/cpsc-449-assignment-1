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
and then run the following commands after you've built the containers:

```bash
$ docker exec -it cpsc-449-1-app /bin/zsh
$ flask-run
```

## Applying Migrations

When making changes to the models, it is important to generate and run migrations.

```bash
$ poetry run flask db migrate
$ poetry run flask db upgrade
```

## Accessing Swagger

`http://localhost:5001/api/docs`

1. Create a new user
2. Login with the new user
3. Copy the token received
4. Click on the Authorize button on the top right corner and enter `Token <token>` and click Authorize

## Adding Dependencies with Poetry

`poetry add <package-name>`
