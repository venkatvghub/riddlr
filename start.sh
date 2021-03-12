#! /bin/bash
# Start-up script for the server.
# Runs on Guincorn with 32 workers.
# The default port is 80.

gunicorn --access-logfile /tmp/flask-access.log --error-logfile /tmp/flask-error.log --bind 0.0.0.0:8082 --workers 32 game:app
