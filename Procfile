web: gunicorn ocr.wsgi:application --log-file - --bind 127.0.0.1:8000
worker: python manage.py qcluster
