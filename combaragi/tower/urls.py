# -*- coding: utf-8 -*-
# Author: UNKI

from django.conf.urls.defaults import patterns, include, url
from tower.views import *

from django.contrib import admin
admin.autodiscover()

# 컴바라기 탑
# 여러개의 탑을 만들 수 있으며 각 탑은 꼭대기 까지 클리어하면 하나의 업적이 생긴다.
urlpatterns = patterns('',
  url(r'^$', main, name='tower-main'),
  url(r'^create/$', create_tower, name='tower-create-tower'),
  url(r'^guards/$', guards, name='tower-guards'),
  url(r'^guards/create/$', create_guard, name='tower-create-guard'),
  url(r'^guards/(?P<gid>\d+)/$', info_guard, name='tower-info-guard'),
  url(r'^guards/(?P<gid>\d+)/action_image/add/$', create_action_image, name='tower-create-action-image'),
  url(r'^(?P<tower_slug>\w+)/$', info, name='tower-info'),
  url(r'^(?P<tower_slug>\w+)/modify/$', modify_tower, name='tower-modify'),
  url(r'^(?P<tower_slug>\w+)/(?P<lv>\d+)/$', level, name='tower-level'),
  url(r'^(?P<tower_slug>\w+)/(?P<lv>\d+)/message/add/$', message_add, name='tower-add-message'),
  url(r'^(?P<tower_slug>\w+)/(?P<lv>\d+)/message/add/(?P<order>reverse)/$', message_add, name='tower-add-message-reverse'),
  url(r'^(?P<tower_slug>\w+)/create/$', create_level, name='tower-create-level'),
  url(r'^(?P<tower_slug>\w+)/open/$', open, name='tower-open'),
)
