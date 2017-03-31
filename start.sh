#! /bin/bash
# Start-up script for the server.
# Runs on Guincorn with 32 workers.
# The default port is 80.

nohup gunicorn --access-logfile /tmp/flask-access.log --error-logfile /tmp/flask-error.log --bind 0.0.0.0:80 --workers 32 hame:app &
