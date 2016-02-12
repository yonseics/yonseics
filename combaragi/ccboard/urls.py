# -*- coding: utf-8 -*-
# Author: UNKI

from django.conf.urls import patterns, url
from ccboard.views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
  url(r'^$', main_page),                  # 메인 페이지
  url(r'^qSearch/(?P<boardname>\w+)/$', bulletin_ac),  # 자동완성 테스트
  url(r'^uSearch$', user_ac),              # 자동완성 테스트
  url(r'^deleteTag/(?P<tid>\d+)/$', delete_tag_page_ajax),  # 태그 삭제(Ajax)
  url(r'^notice_in/(?P<bid>\d+)/$', notice_in_ajax, name='notice-in-ajax'),    # 공지로 올리기(Ajax)
  url(r'^notice_out/(?P<bid>\d+)/$', notice_out_ajax, name='notice-out-ajax'),  # 공지에서 내리기(Ajax)
  url(r'^scrap/(?P<bid>\d+)/$', scrap_ajax, name='board-scrap-ajax'),        # 게시물 스크랩(Ajax)
  url(r'^like/(?P<bid>\d+)/$', like_ajax, name='board-like-ajax'),        # 게시물 좋아요(Ajax)
  url(r'^read/(?P<bid>\d+)/$', direct_read),        # 게시물 번호로 직접 읽기
  url(r'^comment/(?P<bid>\d+)/ajax_append/$', comment_append_ajax),      # 댓글달기(Ajax)
  url(r'^comment/(?P<cid>\d+)/ajax_delete/$', comment_delete_ajax),      # 댓글삭제(Ajax)
  url(r'^(?P<boardname>\w+)/$', list_page, name='board-list'),      # 게시물 리스트 (\w: 영문,숫자, 혹은 밑줄 하나)
  url(r'^(?P<boardname>\w+)/write/new/$', write_page, name='board-write'),  # 게시물 쓰기 (\w: 영문,숫자, 혹은 밑줄 하나)
  url(r'^(?P<boardname>\w+)/read/(?P<bid>\d+)/$', read_page, name='board-read'),    # 게시물 읽기
  url(r'^(?P<boardname>\w+)/modify/(?P<bid>\d+)/$', modify_page, name='board-modify'),    # 게시물 수정
  url(r'^(?P<boardname>\w+)/delete/(?P<bid>\d+)/$', delete_page, name='board-delete'),    # 게시물 삭제
  url(r'^(?P<boardname>\w+)/deleteComment/(?P<bid>\d+)/(?P<cid>\d+)/$', delete_comment_page, name='board-comment-delete'),    # 댓글 삭제
  #url(r'^(?P<boardname>\w+)/notice_out/(?P<bid>\d+)/$', notice_out_ajax, name='notice_out_ajax'),    # 게시물 삭제
  url(r'^(?P<boardname>\w+)/file/delete/(?P<fid>\d+)/$', delete_file_page, name='board-file-delete'),    # 파일 삭제
  url(r'^(?P<boardname>\w+)/addTag/(?P<bid>\d+)/(?P<pid>\d+)/(?P<pidx>\d+)/$', add_tag_page, name='board-tag-add'),      # 태그 추가
]
