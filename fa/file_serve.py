#    Copyright (C) 2009 William.os4y@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import mimetypes
import os
import socket
import time
import traceback
import urllib2

USER_AGENT  = 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'

class ServeStatic:
    def __init__(self, rootpath, realpath, maxage=None, timeout=5):
        self.rootpath = rootpath
        self.realpath = realpath
        self.maxage = maxage
        self.timeout = timeout

    def __call__(self, environ, start_response):
        file_data = self.get_file(environ['PATH_INFO'])

        if not file_data:
            start_response('404 File not found', [])
            return []

        if environ.get('HTTP_IF_NONE_MATCH', 'NONE') != file_data['fmtime']:
            headers = []

            if self.maxage:
                headers.append((
                    'Cache-control',
                    'max-age={}'.format(self.maxage + time.time()),
                ))

            headers.append(('Content-Type', file_data['ftype']))
            headers.append(('ETag', file_data['fmtime']))
            headers.append(('Content-Length', file_data['fsize']))
            start_response('200 OK', headers)
            return file_data['fd']

        start_response('304 Not Modified', [])
        file_data['fd'].close()
        return []

    def get_file(self, url):
        url_path    = urllib2.quote(url, '/:@')
        local_path  = self.rootpath + url_path

        if not os.path.isfile(local_path):
            local_dir   = os.path.dirname(local_path)

            if not os.path.isdir(local_dir):
                os.makedirs(local_dir)

            real_url    = self.realpath + url_path
            request_obj = urllib2.Request(real_url)
            request_obj.add_header('User-Agent', USER_AGENT)

            try:
                opener      = urllib2.build_opener()
                raw_data_d  = opener.open(request_obj, timeout=self.timeout)
                raw_data    = raw_data_d.read()
            except urllib2.HTTPError as error:
                raw_data    = error.read()
            except socket.timeout as error:
                print 'Fetch timeout: ' + real_url
                return None
            except Exception:
                traceback.print_exc()
                return None

            with open(local_path, 'wb') as f:
                f.write(raw_data)

        file_data = {
            'fd'        : open(local_path, 'rb'),
            'fmtime'    : str(os.path.getmtime(local_path)),
            'ftype'     : mimetypes.guess_type(local_path)[0],
            'fsize'     : os.path.getsize(local_path),
        }

        return file_data
