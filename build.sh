#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Current directory: $(pwd)"
echo "Listing files:"
ls -la

pip install -r requirements.txt

echo "Changing to TripleG directory"
cd TripleG
echo "Current directory after cd: $(pwd)"
echo "Listing TripleG files:"
ls -la

python manage.py collectstatic --no-input
python manage.py migrate