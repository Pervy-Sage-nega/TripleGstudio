#!/usr/bin/env bash
# Render.com build script for Triple G Blog

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files (including media)
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

echo "✅ Build completed successfully!"
