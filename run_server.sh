#!/bin/bash
#
# run_server.sh
#
# Starts the Flask server.
#
###

ENV=$1
PORT=$2

if [$ENV -eq 'prod'] ; then
    echo "Running Gunicorn production server."
    gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --reload main:app
else
    echo "Running default development server."
    flask run --host=0.0.0.0 --port=$PORT
fi