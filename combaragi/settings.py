# -*- coding: utf-8 -*-

# Django settings for combaragi project.
import os
from hashlib import md5
from random import random
ROOT_PATH = os.path.dirname(__file__)
from community.utils import get_image_path

DEBUG = True        # 상용이므로 False
TEMPLATE_DEBUG = DEBUG
HTTPS_SUPPORT = False
#SEND_BROKEN_LINK_EMAILS = True         # 이걸 True로 설정하면 링크가 깨지는 게 전부 메일로 옵니다.

DOMAIN_URL = 'yonseics.net'

ADMINS = (
  ('Lim seung-kee', 'limsungkee@gmail.com'),
  ('Admin', 'noreply.combaragi@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': ROOT_PATH+'/combaragi.db',    # MySQL일 경우 DB에서 create database combaragi_test collate=utf8_general_ci로 만들어줍시다.
    'USER': '',            # Not used with sqlite3.
    'PASSWORD': '',          # Not used with sqlite3.
    'HOST': '',            # Set to empty string for localhost. Not used with sqlite3.
    'PORT': '',            # Set to empty string for default. Not used with sqlite3.
  }
}
# DB에서 한글을 사용하기 위한 옵션입니다.
DATABASE_OPTIONS = {"charset":"uft8"}

# 한국 시간대
TIME_ZONE = 'Asia/Seoul'

# 한국어
LANGUAGE_CODE = 'ko-kr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ROOT_PATH+'/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
#m = md5()
#m.update(str(random()))
#STATIC_URL = '/%s/' % m.hexdigest()
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
  # Put strings here, like "/home/html/static" or "C:/www/django/static".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
  ROOT_PATH+'/static',
  ROOT_PATH+'/simplewiki/media',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#  'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# 로그인 관련 변수들
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/'

FIXTURE_DIRS = (
   ROOT_PATH+'/fixtures/',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!s2fr@wt)iv5-z#_5#$%i7iq6kep39j(lkgr-(x8-v!8zuek%g'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
#   'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
  'django.core.context_processors.static',
  'django.contrib.messages.context_processors.messages',
  'combaragi.context_processor.all_boards',
  #'combaragi.community.context_processor.chat',
)

# 가능하면 모듈은 abc순서로 정렬하기 바랍니다.
# SessionMiddleware는 반드시 AuthenticationMiddleware보다 앞에 와야 합니다.
MIDDLEWARE_CLASSES = (
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.middleware.locale.LocaleMiddleware',
  #'combaragi.community.middleware.ChatCookieMiddleware',
)

AUTH_PROFILE_MODULE = "community.UserProfile"

ROOT_URLCONF = 'combaragi.urls'

TEMPLATE_DIRS = (
  ROOT_PATH + '/templates',
  ROOT_PATH + '/simplewiki/templates',
)

# 가능하면 모듈은 abc순서로 정렬하기 바랍니다.
INSTALLED_APPS = (
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'combaragi.community',    # 커뮤니티. 기본이 되는 App
  'combaragi.ccboard',    # 컴바라기 게시판
  'combaragi.mail',      # 메일 보내기
  'combaragi.mentoring',    # 멘토링
  'combaragi.group',      # 그룹
  'combaragi.tower',      # 탑
  'combaragi.rendertext',      # 글씨를 그림으로
  'combaragi.bomb',
  'photologue',        # 포토로그
  'tagging',          # 태깅
  'simplewiki',
  'tastypie',         # Api
  # Uncomment the next line to enable admin documentation:
  # 'django.contrib.admindocs',
)

# 이메일 보내기
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'noreply.combaragi@gmail.com'
#EMAIL_HOST_PASSWORD = 'igarabmoc'
#EMAIL_USE_TLS = True

# 개인정보 변수
GALLERY_SAMPLE_SIZE = 7

# ccboard 변수
CAN_MODIFY_DAYS = 365     # 이 날짜 이상이 지나면 수정할 수 없게 됩니다.
POINT_BULLETIN = 5         # 글 쓰면 포인트
POINT_COMMENT = 2         # 댓글 쓰면 포인트
BULLETIN_PER_PAGE = 10    # 한 페이지에 글이 몇개 들어가는가?
MAX_A_FILE_SIZE = 100 * 1024 * 1024 # 100MB
MAX_TOTAL_FILE_SIZE = 100 * 1024 * 1024 # 100MB
MAX_QUESTION_LENGTH = 20

# photologue 셋팅
PHOTOLOGUE_MAXBLOCK = 256 * 2 ** 10
PHOTOLOGUE_DIR = 'photologue'
PHOTOLOGUE_PATH = get_image_path

# 멘토링 셋팅
QUESTION_PER_PAGE = 10      # 한 페이지에 질문글이 몇개 보일 것인가?

#NAVER_MAP_KEY = 'ec00fb37b3ceb66fe6b46325d034f006'    # localhost
NAVER_MAP_KEY = 'e102a48a1d90e3d39471a2a7da18ffff'    # yonseics.net

# 글 별 캐시 시간
SIMPLE_CACHE_SECONDS = 3600 * 60

# ranking 셋팅
RANKING_MAX_SIZE = 400
TOP_N = 10

# Tower 세팅
#HINT_DELAY_SECOND = 3600 * 24 * 1  # 1일

RENDERTEXT_FONTMAP = {
  'ygo110': ROOT_PATH+'/fonts/ygo110.ttf',
  'ygo120': ROOT_PATH+'/fonts/ygo120.ttf',
  'ygo130': ROOT_PATH+'/fonts/ygo130.ttf',
  'ygo140': ROOT_PATH+'/fonts/ygo140.ttf',
  'inter': ROOT_PATH+'/fonts/interparkBold.ttf',
}

HINT_DELAY_SECOND = 10  # 10초

# Bomb
BOMB_TIME_DAYS = 7
BOMB_ALARM_BEFORE = [(1, 0, 0), (0, 12, 0)]
BOMB_SPACE_PERSONAL = 10 * 1024 * 1024 # 10MB
