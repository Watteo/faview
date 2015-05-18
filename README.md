# FAView - Use it just like [FAExport](http://faexport.boothale.net/)!

This project builds upon the FAExport API to provide a renewed graphical
interface to FA. The responsive style is provided by
[Materialize](http://materializecss.com/), a CSS framework inspired by Google's
Material Design. JavaScript tricks are provided by Materialze and
[jQuery](https://jquery.com/).

On the server side, the website runs on [Django](https://www.djangoproject.com/)
plus [FAPWS](http://www.fapws.org/). Caching is handled by a Redis daemon.

Since nothing is perfect, I must point out an important flaw: the server caches
all resources (images, audio, etc) on the local directory before serving them
to clients. The current cache system is not multi-threaded (yet), and fetches
remote files only when requested (after you load the page text).

## Install

* System-wide requirements: `python2.7 pip virtualenv libev-dev redis-server`
* On a directory of your choosing execute the following commands:

  ```shell
  virtualenv website
  cd website
  source bin/activate
  ```

* Clone this repo to your `website` directory, you should end up with something
  like `website/faview/{manage.py,runserver.py,etc}`.
* Use pip to install some needed python libraries. **Note:** if you're upgrading
  from a previous version make sure to run this command again.

  ```shell
  pip install -r faview/requirements.txt
  ```

* You should be ready now, run `python runserver.py`
* Go to `localhost:8080` to test if it's working.

## Configuration

When running the server with `runserver.py` you may set the environment
variables `FAVIEW_IP` and `FAVIEW_PORT` to specify a different IP/Port to
listen.
