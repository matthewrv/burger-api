#!/usr/bin/env sh

# pleh.sh - It is like "help", but backwards. Contains shortcuts for useful commands.

COMMAND="$1";
shift 1

PYTHONPATH=$PWD:$PYTHONPATH
STATUS=0

CONTAINER_NAME=postgres-burger
DB_NAME=`dotenv get DB_NAME`
DB_USER=`dotenv get DB_USER`
DB_PASSWORD=`dotenv get DB_PASSWORD`

start_env() {
    docker container run \
        --name $CONTAINER_NAME \
        -p 5432:5432 \
        -e POSTGRES_DB=${DB_NAME} \
        -e POSTGRES_USER=${DB_USER} \
        -e POSTGRES_PASSWORD=${DB_PASSWORD} \
        -d \
        postgres:17.4-alpine
}

stop_env() {
    docker container stop $CONTAINER_NAME
    docker container rm $CONTAINER_NAME
}

case $COMMAND in
    "format")
        echo "Formatting code..."
        ruff format;
        ruff check --select I --fix
        ruff check --fix -s
        ;;

    "script")
        echo "Executing script..."
        python $@
        ;;

    "test")
        echo "Running tests..."
        echo
        echo "Mypy running..."
        mypy . || STATUS=$?
        echo
        echo "Pytest running..."
        secret_key=testsonlysecretkey pytest $@ || STATUS=$?
        echo
        echo "Ruff running..."
        ruff check || STATUS=$?
        ;;

    "build")
        echo "Build docker image..."
        docker build -t matthewrv/burger-api .
        ;;

    "start-env")
        start_env
        ;;

    "stop-env")
        stop_env
        ;;

    "run")
        echo "Starting docker container with application..."
        docker run --env-file=.env matthewrv/burger-api
        ;;

    *)
        echo "Usage: pleh.sh <command> [OPTIONS]"
        echo
        echo pleh.sh - It is like "help", but backwards. Contains shortcuts for useful commands.
        echo
        echo "Available commands:"
        echo "  format    - Format code using ruff"
        echo "  run       - Run python script with provided options"
        echo "  test      - Run pytest with provided options"
        echo "  build     - Build docker production docker image"
        echo "  start-env - Start postgres db for application from .env config
        echo "  stop-env  - Stop postgres db for application
        ;;
esac

exit $STATUS
