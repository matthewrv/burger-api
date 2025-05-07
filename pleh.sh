#!/usr/bin/env sh

# pleh.sh - It is like "help", but backwards. Contains shortcuts for useful commands.

COMMAND="$1";
if [ "$1" != "" ]; then
    shift 1
fi

PYTHONPATH=$PWD:$PYTHONPATH
STATUS=0

CONTAINER_NAME=postgres-burger
DB_NAME=$([ "$DB_NAME" != "" ] && echo $DB_NAME || dotenv get DB_NAME)
DB_USER=$([ "$DB_USER" != "" ] && echo $DB_USER || dotenv get DB_USER)
DB_PASSWORD=$([ "$DB_PASSWORD" != "" ] && echo $DB_PASSWORD || dotenv get DB_PASSWORD)

start_env() {
    docker ps -a | grep -q $CONTAINER_NAME \
        && docker container start $CONTAINER_NAME \
        || docker container run \
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
    "init-dotenv")
        SECRET_KEY=$(openssl rand -hex 32) && \
            cat .env.example | sed -e "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" | tee .env && \
            unset SECRET_KEY ||
            echo ERROR: openssl not found. Install it first.
        ;;

    "start")
        echo "Serving application with uvicorn"
        uvicorn --loop uvloop --log-level info --use-colors main:app
        ;;

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

    "bench")
        cd docs
        docker run \
            -v $(pwd):/var/loadtest \
            -v $SSH_AUTH_SOCK:/ssh-agent -e SSH_AUTH_SOCK=/ssh-agent \
            --net host \
            -it yandex/yandex-tank
        cd ..
        ;;

    "profile")
        py-spy record -o profile.prof --pid $(pgrep uvicorn) --format speedscope -d $1
        ;;

    *)
        echo "Usage: pleh.sh <command> [OPTIONS]"
        echo
        echo pleh.sh - It is like "help", but backwards. Contains shortcuts for useful commands.
        echo
        echo "Available commands:"
        echo "  format      - Format code using ruff"
        echo "  test        - Run pytest with provided options, and mypy/ruff check"
        echo "  script      - Run python script with provided options"
        echo "  init-dotenv - Create .env file from template"
        echo "  build       - Build docker production docker image"
        echo "  run         - Run application in docker container"
        echo "  start-env   - Start postgres db for application from .env config"
        echo "  stop-env    - Stop postgres db for application"
        echo "  bench       - Run perfomance benchmark with docs/load.yaml file"
        echo "  profile     - Run py-spy profiler. Duration of sampling is required"
        ;;
esac

exit $STATUS
