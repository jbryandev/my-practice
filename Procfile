web: gunicorn mypractice.wsgi --log-file -
worker: celery -A mypractice worker -l info --without-heartbeat -E -P solo