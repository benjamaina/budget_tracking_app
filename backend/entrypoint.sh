#!/bin/sh
set -e

# wait-for-db (simple loop)
echo "Waiting for database..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.5
done
echo "Database up"

# run migrations
python manage.py migrate --noinput

# collect static
python manage.py collectstatic --noinput

# start Gunicorn
exec gunicorn budgetapp.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --log-level info
