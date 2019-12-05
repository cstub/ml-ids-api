#!/bin/bash

gunicorn --bind 0.0.0.0:5000 -w 5 -k gevent wsgi:app