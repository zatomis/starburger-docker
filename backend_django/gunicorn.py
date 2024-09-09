from multiprocessing import cpu_count
from os import environ


#bind = '127.0.0.1:' + environ.get('PORT', '8000')
bind = '0.0.0.0:' + environ.get('PORT', '8000')
print(f"Gunicorn = {bind}")
max_requests = 1000
worker_class = 'gevent'
workers = cpu_count()
env = {
    'DJANGO_SETTINGS_MODULE': 'star_burger.settings'
}
reload = True
name = 'star_burger'
