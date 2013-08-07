# -*- coding: utf-8 -*-
# Author: UNKI

from django.conf.urls.defaults import patterns, url
from group.views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^$', main_page, name='group'),                  # 메인 페이지
  url(r'^(?P<gid>\d+)/$', group_main_page, name='group_main'),        # 해당 그룹 메인 페이지
  url(r'^create/$', create_page, name='group_create'),            # 그룹 새로 생성
  url(r'^(?P<gid>\d+)/enter/$', enter_page, name='group_enter'),        # 그룹 가입
  (r'^(?P<gid>\d+)/leave/$', leave_page),        # 해당 그룹에서 나옴
  url(r'^(?P<gid>\d+)/remove/$', remove_page, name='group_remove'),        # 해당 그룹을 삭제
  url(r'^(?P<gid>\d+)/manage/$', manage_page, name='group_manage'),      # 그룹 관리
  url(r'^(?P<gid>\d+)/invite/$', invite_page, name='group_invite'),      # 초청
  url(r'^(?P<gid>\d+)/invite/(?P<sidHash>\w+)/$', invite_ajax, name='group_invite_ajax'),      # 초청_ajax
  url(r'^(?P<gid>\d+)/board/$', board_page, name='group_board'),        # 그룹 게시판
  url(r'^(?P<gid>\d+)/chat/$', chat_page, name='group_chat'),        # 그룹 게시판
  url(r'^(?P<gid>\d+)/members/$', members_page, name='group_members'),      # 회원명부 게시판
  url(r'^(?P<gid>\d+)/kick/(?P<uid>\d+)/$', kick_page, name='group_kick'),      # 회원 강제 탈퇴
  (r'^qSearch$', autocomplete),          # 이름 자동완성
)
