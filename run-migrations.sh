#!/bin/bash
# run-migrations.sh
# Script to run migrations and create superuser on Render

echo "Running Django migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Migrations completed successfully!"
