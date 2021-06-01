web: gunicorn mypractice.wsgi --log-file node --inspect=8080 index.js
worker: celery -A mypractice worker -l info --beat --without-heartbeat -E -P solo