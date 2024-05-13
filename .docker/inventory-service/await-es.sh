#!/bin/bash

# Environment variables passed from docker-compose

set -e

echo "Waiting for Elasticsearch to start..."
until curl -s "$ELASTICSEARCH_HEALTH_ENDPOINT" | jq -e '.status == "yellow" or .status == "green"' > /dev/null; do
    >&2 echo "Elasticsearch is unavailable - sleeping"
    sleep 1
done

>&2 echo "Elasticsearch is ready"
