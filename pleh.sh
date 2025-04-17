#!/usr/bin/env bash

# pleh.sh - It is like "help", but backwards. Contains shortcuts for useful commands.

COMMAND="$1";
shift 1

PYTHONPATH=$PWD:$PYTHONPATH

case $COMMAND in
    "format")
        echo "Formatting code..."
        ruff format;
        ruff check --select I --fix
        ;;

    "run")
        echo "Executing script..."
        python $@
        ;;
        
    "test")
        echo "Running tests..."
        pytest $@
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
        ;;
esac
