# -*- coding: utf-8 -*-
# Author: UNKI
from datetime import timedelta, datetime

from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from django.contrib.auth.models import User
from photologue.models import Gallery, Photo
from ccboard.multifile import MultiFileField
from os.path import isfile
from os.path import splitext
from os import remove as file_remove

# Caching
from django.core.cache import cache
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.query import QuerySet

IMAGE_GROUP = ['.jpg', '.png', '.gif']

class Board(models.Model):  # 게시판
  name = models.CharField(max_length=20, unique=True)    # 게시판의 ID (ex. freeboard)
  title = models.CharField(max_length=30)    # 게시판의 실제 이름 (ex. 자유게시판)
  staff = models.BooleanField(default=False)  # 운영자 게시판인가
  allowAnom = models.BooleanField(default=True)  # 익명을 허용하는가?
  secret = models.BooleanField(default=False)    # 숨겨진 게시판인가
  desc = models.CharField(max_length=80)    # 게시판의 자세한 설명
  updated = models.DateTimeField(auto_now_add=True, auto_now=True)    # 업데이트된 날짜
  #mode = models.CharField(max_length=10, null=True, blank=True)    # 게시판의 형태(일반적으로 없으면 기본 게시판 형태)

  def __unicode__(self):
    return self.title

  def is_new(self):
    return (datetime.now()-timedelta(days=1)) < self.updated

# 태그는 아직 안 씁니다.
#class TagModel(models.Model):  # 태그들
#  title = models.CharField(max_length=20, null=False)
#  def __unicode__(self):
#    return self.title

class Category(models.Model):
  board = models.ForeignKey(Board, related_name='categories')        # 게시판 외래키
  title = models.CharField(max_length=20, null=False)
  def __unicode__(self):
    return '[%s] %s'%(self.board.title, self.title)
    #return self.title

###################### Bulletin ##################
class SimpleCacheQuerySet(QuerySet):
  def filter(self, *args, **kwargs):
    pk = None
    for val in ('pk', 'pk__exact', 'id', 'id__exact'):
      if val in kwargs:
        pk = kwargs[val]
        break
    if pk is not None:
      opts = self.model._meta
      key = '%s.%s:%s' % (opts.app_label, opts.module_name, pk)
      obj = cache.get(key)
      if obj is None:
        obj = Bulletin.base_objects.get(id=pk)
        cache.set(key_from_instance(obj), obj, SIMPLE_CACHE_SECONDS)
      self._result_cache = [obj]
    return super(SimpleCacheQuerySet, self).filter(*args, **kwargs)

class SimpleCacheManager(models.Manager):
  def get_query_set(self):
    return SimpleCacheQuerySet(self.model)

class BulletInManager(SimpleCacheManager):
  def get_query_set(self):
    return super(BulletInManager, self).get_query_set().filter(Q(parent=None))

class NoticeManager(SimpleCacheManager):
  def get_query_set(self):
    return super(NoticeManager, self).get_query_set().filter(Q(parent=None, notice=True, deleted=False))

class CommentManager(SimpleCacheManager):
  def get_query_set(self):
    return super(CommentManager, self).get_query_set().exclude(parent=None)

class Bulletin(models.Model):  # 게시물이자 comment. parent가 있으면 comment이다.
  board = models.ForeignKey(Board)        # 게시판 외래키
  writer = models.ForeignKey(User, null=True, related_name='my_bulletins')    # 글쓴이. 글쓴이가 없으면 익명사용자이다.
  category = models.ForeignKey(Category, null=True, blank=True, related_name='related_bulletin')      # 카테고리
  parent = models.ForeignKey('self', null=True, blank=True, related_name='my_comments')  # 현 게시물의 부모
  title = models.CharField(max_length=100)    # 게시물 제목
  content = models.TextField(null=False)      # 게시물 내용
  created = models.DateTimeField(auto_now_add=True)  # 만들어진 날짜
  updated = models.DateTimeField(auto_now=True)    # 업데이트된 날짜
  writerIP = models.CharField(null=True, blank=True, max_length=15)  # 글쓴이 IP
  isHiddenUser = models.BooleanField(default=False,null = False)  # 익명사용자 여부
  hits = models.IntegerField(default=0)          # 조회수
  deleted = models.BooleanField(default=False)      # 삭제되었나?
  secret = models.BooleanField(default=False)        # 비밀글 여부(글이라면 운영자와 글쓴이에게 보이고 댓글이라면 원글 작성자와 댓글 작성자에게 보임)
  notice = models.BooleanField(default=False)        # 공지사항인지 여부
  commentCnt = models.PositiveSmallIntegerField(default=0)# 댓글 수
  gallery = models.OneToOneField(Gallery, null=True, blank=True)    # 갤러리
  file = MultiFileField()  # 업로드된 파일
  base_objects = models.Manager()
  objects = SimpleCacheManager()
  bulletIns = BulletInManager()
  comments = CommentManager()
  notices = NoticeManager()
  rate = models.IntegerField(default=0, null=True, blank=True)
  #tags = models.ManyToManyField(TagModel, null=True)
  class Meta:
    ordering = ["-created"]

  def __unicode__(self):
    return ' >> '.join([ self.board.title, self.title ])

  def get_writerIP(self):
    return self.writerIP[-7:]

  def get_writer_introduction(self):
    if not self.isHiddenUser:  # 익명 유저라는 표시가 안되어있다면 실명이다
      return self.writer.get_profile().introduction
    else:            # 이거면 익명이다.
      return u''

  def get_writerName(self):    # 작성자 이름을 학번+이름으로 하거나 익명으로 합니다.
    if not self.isHiddenUser:  # 익명 유저라는 표시가 안되어있다면 실명이다
      return self.writer.get_profile().get_full_name()
    else:            # 이거면 익명이다.
      return u'익명사용자'

  def get_pure_writer_name(self):    # 작성자 이름을 학번+이름으로 하거나 익명으로 합니다.
    if not self.isHiddenUser:  # 익명 유저라는 표시가 안되어있다면 실명이다
      return self.writer.get_profile().get_pure_full_name()
    else:            # 이거면 익명이다.
      return u'익명사용자'

  def get_portrait_url(self):
    if not self.isHiddenUser:  # 익명 유저라는 표시가 안되어있다면 실명이다
      return self.writer.get_profile().get_portrait_url()
    return settings.STATIC_URL + 'images/anonymous.jpg'

  def get_portrait_thumbnail(self):
    if not self.isHiddenUser:  # 익명 유저라는 표시가 안되어있다면 실명이다
      return self.writer.get_profile().get_portrait_thumbnail()
    return settings.STATIC_URL + 'images/avatar.jpg'

  def get_recent_comments(self):
    return self.my_comments.filter(updated__gte=self.updated-timedelta(days=1)).order_by('created')

  def get_total_filesize(self):
    return self.files.aggregate(Sum('size'))['size__sum']

  def get_full_title(self):
    if self.category:
      return "[%s]%s" % (self.category.title, self.title)
    return self.title

  def get_last_comment_id(self):
    if self.my_comments.exists():
      return self.my_comments.all()[0].id
    return 0

  def is_new(self):
    return (datetime.now()-timedelta(days=1)) < self.updated

  # 본인의 글인가?
  def isMyBulletin(self, user):
    return self.writer == user
  def isMyComment(self, user):
    return self.isMyBulletin(user)

  # 현재 유저가 해당 글을 읽을 권한이 있는가?
  def hasAuthToRead(self, user):
    board = self.board
    if self.isMyBulletin(user):    # 자기 자신이면 무조건 볼 수 있다.
      return True
    if board.staff:          # 관리자만 볼수 있는 글
      return user.is_staff
    if self.secret:        # 비밀글일 경우
      if self.parent:     # 댓글일 경우
        return self.parent.isMyBulletin(user)     # 원글 쓴 사람은 볼 수 있다.
      else:            # 그냥 글의 경우
        return user.is_staff   # 관리자만 볼 수 있다.
    if self.parent and self.parent.secret:    # 댓글의 경우 원글이 비밀이고 여태 통과 못했으면 못봄
      return False
    return True            # 비밀글도 아니고 뭣도 아닌 경우

SIMPLE_CACHE_SECONDS = getattr(settings, 'SIMPLE_CACHE_SECONDS', 2592000)

def key_from_instance(instance):
  opts = instance._meta
  return '%s.%s:%s' % (opts.app_label, opts.module_name, instance.pk)

def post_save_cache(sender, instance, **kwargs):
  cache.set(key_from_instance(instance), instance, SIMPLE_CACHE_SECONDS)
post_save.connect(post_save_cache, sender=Bulletin)

def pre_delete_uncache(sender, instance, **kwargs):
  cache.delete(key_from_instance(instance))
pre_delete.connect(pre_delete_uncache, sender=Bulletin)

class Rate(models.Model):
  rate = models.IntegerField(default=0, null=True, blank=True)
  bulletin = models.ForeignKey(Bulletin, related_name='rates')

class RelatedFile(models.Model):
  board = models.ForeignKey(Board)
  bulletin = models.ForeignKey(Bulletin, related_name='files')
  file = models.FileField(upload_to='uploaded/%Y/%m/%d')  # 업로드된 파일
  size = models.IntegerField()

  def __unicode__(self):
    return self.file.name.split('/')[-1]

  def delete(self, using=None):
    if isfile(self.file.path):
      file_remove(self.file.path)    # 실제 파일 delete
    super(RelatedFile, self).delete(using)

  def isImage(self):
    return splitext(self.file.name)[1].lower() in IMAGE_GROUP

  def get_name(self):
    return self.file.name.split('/')[-1]

class RelatedPosition(models.Model):
  bulletin = models.ForeignKey(Bulletin, related_name='positions')
  title = models.CharField(max_length=40, null=True, blank=True)    # 위치 이름
  position = models.CharField(max_length=15) # 네이버 맵 관련 자신의 위치

  def __unicode__(self):
    return ' >> '.join([self.bulletin.title, self.title])

class PhotoTag(models.Model):
  photo = models.ForeignKey(Photo, related_name='photo_tags')
  title = models.CharField(max_length=20)    # 태그 이름
  x = models.IntegerField()
  y = models.IntegerField()
  w = models.IntegerField()
  h = models.IntegerField()

  def __unicode__(self):
    return ' >> '.join([self.photo.title,self.title])

# 글 스크랩하기
class Scrap(models.Model):
  bulletin = models.ForeignKey(Bulletin, related_name='scraps')
  user = models.ForeignKey(User)
  created = models.DateTimeField(auto_now_add=True)
  class Meta:
    ordering = ["-created"]
  def __unicode__(self):
    return '님의 스크랩: '.join([self.user.first_name, self.bulletin.title])

# 글 좋아요하기
class Like(models.Model):
  bulletin = models.ForeignKey(Bulletin, related_name='likes')
  user = models.ForeignKey(User)
  created = models.DateTimeField(auto_now_add=True)
  class Meta:
    ordering = ["-created"]
  def __unicode__(self):
    return '님의 좋아요: '.join([self.user.first_name, self.bulletin.title])

