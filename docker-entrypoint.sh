#!/bin/sh
set -e
python manage.py migrate --noinput
# Adds Django's admin CSS/JS to ./static. Never pass --clear: that folder
# also holds the site's own files (PDFs, media), which are not in git.
python manage.py collectstatic --noinput
exec "$@"
