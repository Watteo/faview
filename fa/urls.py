from django.conf.urls import url
from fa import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^user/(?P<name>[-_.~\[\]\w]+)/$', views.user),
    url(r'^user/(?P<name>[-_.~\[\]\w]+)/(?P<folder>gallery)/$', views.gallery),
    url(r'^user/(?P<name>[-_.~\[\]\w]+)/(?P<folder>scraps)/$', views.gallery),
    url(r'^user/(?P<name>[-_.~\[\]\w]+)/(?P<folder>favorites)/$', views.gallery),
    url(r'^user/(?P<name>[-_.~\[\]\w]+)/(?P<watch_view>watchers)/$', views.watch),
    url(r'^user/(?P<name>[-_.~\[\]\w]+)/(?P<watch_view>watching)/$', views.watch),
    url(r'^user/(?P<name>[-_.~\[\]\w]+)/journals/$', views.journals),
    url(r'^submission/(?P<sub_id>[0-9]+)/$', views.submission),
    url(r'^journal/(?P<journ_id>[0-9]+)/$', views.journal),
    url(r'^search/$', views.search),
]
