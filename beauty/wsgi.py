import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty.settings')

import django
django.setup()

import os
import socketio
from chat.views import sio
from django.core.wsgi import get_wsgi_application

import eventlet

application = socketio.WSGIApp(sio, get_wsgi_application())
eventlet.wsgi.server(eventlet.listen(('', 8003)), application)
