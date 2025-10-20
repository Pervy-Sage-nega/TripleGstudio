#!/usr/bin/env bash
cd TripleG
gunicorn config.wsgi:application