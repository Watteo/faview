# FAView - Use it just like [FAExport](http://faexport.boothale.net/)!

This project builds upon the FAExport API to provide a renewed graphical
interface to FA. The responsive style is provided by
[Materialize](http://materializecss.com/), a CSS framework inspired by Google's
Material Design. Finally, the JavaScript tricks are provided by Materialze and
[jQuery](https://jquery.com/).

On the server side, the website runs on [Django](https://www.djangoproject.com/)
plus [FAPWS](http://www.fapws.org/). Caching is handled by a memcached daemon.

Since nothing is perfect, I must point out an important flaw: you cannot (and
should not steal other website's bandwith (indiscriminately) so the server
caches all resources (images, audio, etc) on the local directory before serving
them to clients. This was done so that you can run the service on your main
machine and use it from a mobile device on your LAN with little added delay.

## Install

* System-wide requirements: `python2.7 pip virtualenv libev-dev memcached`
* On a directory of your choosing execute the following commands:

  ```shell
  virtualenv website
  cd website
  source bin/activate
  ```

* Clone this repo to your `website` directory, you should end up with something
  like `website/faview/{manage.py,runserver.py,etc}`.
* Use pip to install some needed python libraries.

  ```shell
  pip install -r faview/requirements.txt
  ```

* You should be ready now, run `python runserver.py`
* Go to `localhost:8080` to test if it's working.
