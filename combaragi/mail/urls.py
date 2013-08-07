# -*- coding: utf-8 -*-
# Author: UNKI

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from mail.views import main_page
import os
ROOT_PATH = os.path.dirname(__file__)

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^$', main_page, name='mail'),                # 메인 페이지
  (r'^thanks/$', direct_to_template, { 'template':'mail/thanks.html' }),    # 메일 전송 완료
  # 여기서 기능들은. 전체 동문에게 편지 보내기. 자기 동기에게 편지 보내기. 특정 사람에게 편지 보내기 등이 있다.
)
