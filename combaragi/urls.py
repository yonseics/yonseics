# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView
from community.feeds import RssFeed, AtomFeed
from community.views import *
from ccboard.views import like_book_page, all_page
# 이 부분은 모듈에서도 사용합니다.
from community.views import meta_page
import os
ROOT_PATH = os.path.dirname(__file__)
from django.contrib import admin
admin.autodiscover()

current_user = CurrentAdmin.objects.all()[0].user

# Django가 기본으로 제공하는 패턴들

urlpatterns = patterns('',
  url(r'^login/$', login_page, {'template_name': 'account/login.html'}, name='login' ),    # 로그인
  url(r'^login_page_(?P<next>.*)_(?P<login_failed>.*)/$', direct_to_template, { 'template':'account/login.html', 'extra_context':{ 'admin_email':current_user.email } }, name='login-page'),
  url(r'^login_page_(?P<next>.*)/$', direct_to_template, { 'template':'account/login.html', 'extra_context':{ 'admin_email':current_user.email } }, name='login-page'),
  (r'^register/success/$', direct_to_template, { 'template':'account/register_success.html' }),
  (r'^meta/$', meta_page),
  # 미디어 폴더에 있는 파일들은 그냥 접근할 수 있게 해줍니다. img, sound등.
  (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
  (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': ROOT_PATH+'/static'}),
  (r'^admin/', include(admin.site.urls)),    # 관리자 권한을 위하여
  (r'^board/', include('combaragi.ccboard.urls')),    # ccboard
  (r'^mail/', include('combaragi.mail.urls')),      # 메일 보내기
  (r'^group/', include('combaragi.group.urls')),      # 소모임 기능
  (r'^mobile/', include('combaragi.mobile.urls')),    # 모바일
  (r'^tower/', include('combaragi.tower.urls')),      # 탑
  (r'^bomb/', include('combaragi.bomb.urls')),
  (r'^wiki/', include('simplewiki.urls')),
  #(r'^photologue/', include('photologue.urls')),
  (r'^mentoring/', include('mentoring.urls')),
  # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
  (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow:", mimetype="text/plain")),  # robots.txt
)

feeds = {'rss': RssFeed, 'atom': AtomFeed}
handler500 = 'community.views.server_error'

# community.views
# 나중에 request.user가 구현되면 이곳에 pre_login(main_page)와 같이 wrapping을 해 줍니다. 이거 아직은 보류!
urlpatterns += patterns('',
  url(r'^$', main_page, name='home'),    # 메인 페이지
  url(r'^logout/$', logout_page, name='logout'),      # 로그아웃
  (r'^likebook/$', like_book_page),    # 스크랩북
  (r'^allboards/', all_page),        # 모든 게시판 목록
  url(r'^under_construction/$', direct_to_template, { 'template':'under_construction.html' }, name='under_construction'),
  url(r'^account/register/$', register_page, name='register'),    # 회원가입
  url(r'^account/modify/$', info_modify_page, name='account-modify'),    # 정보 수정
  url(r'^account/emblem/$', show_emblem, name='account_emblem'),    # 엠블렘 보기
  url(r'^account/emblem/obtain/(?P<emblem_id>\w+)/$', obtain_emblem, name='emblem_obtain'),    # 엠블렘 얻기
  url(r'^account/emblem/use/(?P<emblem_id>\w+)/$', use_emblem, name='emblem_use'),        # 엠블렘 사용
  url(r'^account/info/(?P<sidHash>\w+)/$', info_page, name='account-info'),    # 정보 수정
  (r'^account/avatar/(?P<uid>\d+)/$', avatar_img),
  (r'^map/position/$', direct_to_template, { 'template':'map/position.html' , 'extra_context':{ 'naver_map_key':settings.NAVER_MAP_KEY } } ),
  (r'^map/show/(?P<x>\d+),(?P<y>\d+)/$', direct_to_template, { 'template':'map/show.html', 'extra_context':{ 'naver_map_key':settings.NAVER_MAP_KEY } } ),
  #(r'^map/all/$', map_show_all),
  (r'^map/print/$', direct_to_template, { 'template':'map/print.html', 'extra_context':{ 'naver_map_key':settings.NAVER_MAP_KEY } } ),
  url(r'^known/$', show_known, name='known_main'),
  (r'^known/add/(?P<sidHash>\w+)/$', add_known),
  (r'^known/remove/(?P<kid>\d+)/$', remove_known),
  url(r'^account/list/$', account_list_page, name='memberlist'),
  url(r'^account/list/(?P<iid>\d+)/$', account_list_page, name='memberlist_page'),
  (r'^account/sid_list/(?P<sid>\d\d)/$', account_sid_list_page),
  url('^ranking/$', ranking_page, name='ranking'),
  (r'^feed/go/(?P<fid>\d+)/$', go_feed_page),
  (r'^feed/del/all/$', del_all_feed_ajax),
  (r'^feed/del/(?P<fid>\d+)/$', del_feed_ajax),
  (r'^feed/third/$', third_feed_ajax),
  (r'^feed/more/content/(?P<bid>\d+)/$', get_more_content_ajax),
  (r'^feed/more/comments/(?P<bid>\d+)/(?P<cnt>\d+)/$', get_more_comments_ajax),
  (r'^feed/more/recent_comments/(?P<bid>\d+)/(?P<lcid>\d+)/$', get_recent_comments_ajax),
  (r'^feed/more/(?P<page>\d+)/$', get_more_feeds_ajax),
  (r'^feed/more/(?P<board_name>\w+)/(?P<page>\d+)/$', get_more_feeds_ajax),
  url(r'^feed/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}, name='feeds'),
  (r'^gcalendar/$', login_required(TemplateView.as_view(template_name="gcalendar/gcalendar.html"))), #@UndefinedVariable
)

# 모듈을 만드는 사람은 반드시 url include에 관하여 공부한 뒤에 모듈을 개발하도록 합니다.
