#!/usr/bin/env sh

# pleh.sh - It is like "help", but backwards. Contains shortcuts for useful commands.

COMMAND="$1";
shift 1

PYTHONPATH=$PWD:$PYTHONPATH
STATUS=0

case $COMMAND in
    "format")
        echo "Formatting code..."
        ruff format;
        ruff check --select I --fix
        ;;

    "script")
        echo "Executing script..."
        python $@
        ;;
        
    "test")
        echo "Running tests..."
        mypy . || STATUS=$?
        pytest $@ || STATUS=$?
        ruff check || STATUS=$?
        ;;

    "build")
        echo "Build docker image..."
        docker build -t matthewrv/burger-api .
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
        echo "  format - Format code using ruff"
        echo "  run    - Run python script with provided options"
        echo "  test   - Run pytest with provided options"
        echo "  build  - Build docker production docker image"
        ;;
esac

exit $STATUS
