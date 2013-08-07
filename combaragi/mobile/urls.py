# -*- coding: utf-8 -*-
# Author: UNKI

from django.conf.urls.defaults import patterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('combaragi.mobile.views',
  (r'^$', 'main_page'),
)

