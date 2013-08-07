# -*- coding: utf-8 -*-
# Author: UNKI

from django.conf.urls.defaults import patterns
from django.contrib import admin
from mentoring.views import main_page, autocomplete, question_write_page, question_read_page, question_modify_page, question_reply_page, question_delete_page, \
              mentors_info_page, register_mentor_page, register_mentee_page, accept_mentee_page, deny_mentee_page, my_mentees_info_page, \
              my_mentors_info_page, list_page

admin.autodiscover()

urlpatterns = patterns('',
  (r'^$', main_page),                # ���� ������
  (r'^search/(?P<type>\w+)/$', autocomplete),
  (r'^question/write/$', question_write_page),
  (r'^question/write/(?P<qid>\d+)/$', question_write_page),
  (r'^question/read/(?P<qid>\d+)/$', question_read_page),
  (r'^question/modify/(?P<qid>\d+)/$', question_modify_page),
  (r'^question/reply/(?P<qid>\d+)/$', question_reply_page),
  (r'^question/delete/(?P<qid>\d+)/$', question_delete_page),
  (r'^info/mentors/$', mentors_info_page),
  (r'^register/mentor/$', register_mentor_page),
  (r'^register/mentee/(?P<mid>\d+)/$', register_mentee_page),
  (r'^register/accept/mentee/(?P<rid>\d+)/$', accept_mentee_page),
  (r'^register/deny/mentee/(?P<rid>\d+)/$', deny_mentee_page),
  (r'^myinfo/mentors/$', my_mentors_info_page),
  (r'^myinfo/mentees/$', my_mentees_info_page),
  (r'^list/(?P<list_type>\w+)/$', list_page),
  (r'^list/(?P<list_type>\w+)/(?P<page>\d+)/$', list_page),
#(r'^(?P<boardname>\w+)/(?P<page>\d+)/addTag/(?P<bid>\d+)/(?P<pid>\d+)/(?P<pidx>\d+)/$', add_tag_page),      # �±� �߰�
)
