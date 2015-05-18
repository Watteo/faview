#!/usr/bin/env python
from django.conf import settings
from fa.file_serve import ServeStatic
from fapws import base
from fapws.contrib import django_handler
import django
import fapws._evwsgi as evwsgi
import os
import sys

MEDIA_PREFIX = {
    'avatar'       : 'http://a.facdn.net',
    'data'         : 'http://d.facdn.net',
    'thumbnail'    : 'http://t.facdn.net',
    'themes'       : 'http://www.furaffinity.net/themes',
}

def start():
    evwsgi.start(
        os.getenv('FAVIEW_IP', '0.0.0.0'),
        os.getenv('FAVIEW_PORT', '8080'),
    )
    evwsgi.set_base_module(base)

    for local_path, real_path in MEDIA_PREFIX.iteritems():
        media_dir = ServeStatic(
            settings.MEDIA_ROOT + local_path,
            real_path,
            maxage = 2629000,
        )
        evwsgi.wsgi_cb((
            settings.MEDIA_URL + local_path,
            media_dir,
        ))

    def generic(environ, start_response):
        res = django_handler.handler(environ, start_response)
        return [res]

    evwsgi.wsgi_cb(('', generic))
    evwsgi.set_debug(0)
    evwsgi.run()

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
    sys.setcheckinterval = 100000
    django.setup()
    start()
