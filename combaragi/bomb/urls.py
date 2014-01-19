
from django.conf.urls.defaults import patterns, url
from ccboard.views import *

from django.contrib import admin
from combaragi.bomb.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', BombListView.as_view(), name='bomb-list'),
    url(r'^create/$', create_bomb_view, name='bomb-create'),
    url(r'^delete/(?P<bid>\w+)/$', delete_bomb_view, name='bomb-delete'),
)
