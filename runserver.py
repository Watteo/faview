#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
sys.setcheckinterval = 100000

import fapws._evwsgi as evwsgi
from fapws.contrib import django_handler, views
from fapws import base
import django
django.setup()

def start():
    evwsgi.start('0.0.0.0', '8080') 
    evwsgi.set_base_module(base)

    static_dir = views.Staticfile('static', maxage=2629000)
    media_dir = views.Staticfile('media', maxage=2629000)

    def generic(environ, start_response):
        res = django_handler.handler(environ, start_response)
        return [res]

    evwsgi.wsgi_cb(('/static', static_dir))
    evwsgi.wsgi_cb(('/media', media_dir))
    evwsgi.wsgi_cb(('', generic))
    evwsgi.set_debug(0)   
    evwsgi.run()
 
if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    start()
