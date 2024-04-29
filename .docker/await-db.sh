#!/bin/bash

# Environment variables passed from docker-compose

set -e

echo "Waiting for MongoDB to start..."
until mongosh "$MONGO_URI/$MONGO_DB_NAME" --eval "db.adminCommand({ ping: 1 })" > /dev/null 2>&1; do
    >&2 echo "MongoDB is unavailable - sleeping"
    sleep 1
done

>&2 echo "MongoDB is up - executing commands"

# Create the new database and add our user if it doesn't exist
mongosh "$MONGO_URI" --username "$MONGO_USER" --password "$MONGO_PASSWORD" --eval "
    db = db.getSiblingDB('$MONGO_DB_NAME');
    if (db.getUser('$MONGO_USER')) {
        print('User $MONGO_USER already exists');
    } else {
        db.createUser({
            user: '$MONGO_USER',
            pwd: '$MONGO_PASSWORD',
            roles: [{ role: 'readWrite', db: '$MONGO_DB_NAME' }]
        });
        print('User $MONGO_USER created with readWrite role on $MONGO_DB_NAME');
    }
" > /dev/null
