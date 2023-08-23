#!/usr/bin/python3

from app import app
from wsgiref.handlers import CGIHandler

try:
    CGIHandler().run(app)
except Exception as e:
    with open("errors.log", "a") as f:
        f.write(str(e))