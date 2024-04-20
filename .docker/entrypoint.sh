#!/bin/bash

socat TCP-LISTEN:27017,fork TCP:fim-mongo:27017 &

# NOTE: This has to go after the socat commands, otherwise the database won't be ready
# The location directly relates to where it was placed from the Dockerfile
sh /docker-build-tools/await-db.sh

# Leave the container running
tail -f /dev/null

# Start the Flask app
# poetry run python app.py
