#!/usr/bin/env bash

# pleh.sh - It is like "help", but backwards. Contains shortcuts for useful commands.

COMMAND="$1";
PYTHONPATH=$PWD:$PYTHONPATH

case $COMMAND in
    "format")
        echo "Formatting code..."
        ruff format;
        ruff check --select I --fix;
        ;;

    "run")
        echo "Executing script..."
        python $2
        ;;
        
    "test")
        echo "Running tests..."
        pytest
        ;;

    *)
        echo "Usage: pleh.sh <command>"
        echo
        echo pleh.sh - It is like "help", but backwards. Contains shortcuts for useful commands.
        echo 
        echo "Available commands:"
        echo "  format - Format code using ruff"
        ;;
esac
