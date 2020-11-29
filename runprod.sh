#!/bin/bash

python3 manage.py qcluster &
gunicorn --bind 0.0.0.0:8000 webhawk.wsgi
