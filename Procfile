release: python manage.py migrate
web: gunicorn config.wsgi --log-file -
worker: python manage.py run_bot
