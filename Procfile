web: gunicorn mypractice.wsgi --log-file -
worker: celery -A mypractice worker -l info --beat --without-heartbeat -E -P solo