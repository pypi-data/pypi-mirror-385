#!/bin/bash

set -e

IMAGE_NAME=postgres-event-store
CONTAINER_NAME=postgres-event-store
SQL_INIT_SCRIPT=init.sql
POSTGRES_PORT=35432
POSTGRES_USER=event_user
POSTGRES_PASSWORD=event_pass
POSTGRES_DB=event_store_db

cleanup() {
    echo "Cleaning up: Stopping and removing Docker container..."
    docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1 || true
}

trap cleanup EXIT

docker build -t $IMAGE_NAME .

if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
    docker rm -f $CONTAINER_NAME > /dev/null
fi

docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$POSTGRES_PORT":5432 \
    -e POSTGRES_USER="$POSTGRES_USER" \
    -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -e POSTGRES_DB="$POSTGRES_DB" \
    -v "$(pwd)/$SQL_INIT_SCRIPT":/docker-entrypoint-initdb.d/init.sql \
    postgres:15.3

until docker exec $CONTAINER_NAME pg_isready -U $POSTGRES_USER > /dev/null 2>&1; do
    sleep 1
    echo "wait is ready"
done

pytest .