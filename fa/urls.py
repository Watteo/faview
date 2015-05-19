from django.conf.urls import url
from fa import views
from fa import fa_api

USER_URL_PATTERN    = r'^user/(?P<name>{})/'.format(fa_api.USER_REGEX_STR)

urlpatterns = [
    url(r'^$', views.index),
    url(USER_URL_PATTERN + r'$', views.user),
    url(USER_URL_PATTERN + r'(?P<folder>gallery)/$', views.gallery),
    url(USER_URL_PATTERN + r'(?P<folder>scraps)/$', views.gallery),
    url(USER_URL_PATTERN + r'(?P<folder>favorites)/$', views.gallery),
    url(USER_URL_PATTERN + r'(?P<watch_view>watchers)/$', views.watch),
    url(USER_URL_PATTERN + r'(?P<watch_view>watching)/$', views.watch),
    url(USER_URL_PATTERN + r'journals/$', views.journals),
    url(r'^submission/(?P<sub_id>[0-9]+)/$', views.submission),
    url(r'^journal/(?P<journ_id>[0-9]+)/$', views.journal),
    url(r'^search/$', views.search),
]
