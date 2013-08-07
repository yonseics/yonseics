# -*- coding: utf-8 -*-
# Author: UNKI

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.aggregates import Max, Min
from django.http import Http404
from photologue.models import Photo


class Guard(models.Model):
  name = models.CharField(max_length=30, verbose_name='지킴이 이름')

  def __unicode__(self):
    return self.name

  def get_action_image(self):
    if self.images.exists():
      return self.images.latest().photo.get_thumbnail_url()
    return settings.STATIC_URL + 'images/avatar.jpg'


class Tower(models.Model):
  DIFFICULTY_CHOICE = (
    (u'E', u'쉬움'),
    (u'M', u'중간'),
    (u'H', u'어려움'),
  )
  slug = models.SlugField(max_length=30, unique=True, verbose_name='영문이름')
  name = models.CharField(max_length=30, verbose_name='탑의 이름')
  owner = models.ForeignKey(User, related_name='my_towers')
  opened = models.BooleanField(default=False)
  guards = models.ManyToManyField(Guard, related_name='guarding_towers', blank=True, null=True, verbose_name='지킴이', help_text='탑의 지킴이는 탑을 정복하는 과정에서 도움을 주는 존재들입니다.')
  image = models.FileField(upload_to='uploaded/%Y/%m/%d', verbose_name='탑 이미지')
  difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICE, verbose_name='난이도')

  def __unicode__(self):
    return self.name

  def max_level(self):
    if self.levels.exists():
      return self.levels.all().aggregate(Max('level'))['level__max']
    return 0

  def min_level(self):
    if self.levels.exists():
      return self.levels.all().aggregate(Min('level'))['level__min']
    return 0


class ActionImage(models.Model):
  guard = models.ForeignKey(Guard, related_name='images')
  name = models.CharField(max_length=30, verbose_name='액션이미지의 이름', help_text='해당 액션 이미지가 나타내는 이름을 정해주세요. 예) 기쁨, 슬픔 등등...')
  photo = models.ForeignKey(Photo, null=True, blank=True)
  class Meta:
    get_latest_by = 'name'

  def natural_key(self):
    return self.photo.image.url, self.guard.id

  def __unicode__(self):
    return u'%s: %s' % (self.guard.name, self.name)

  def get_thumbnail_url(self):
    return self.photo.get_thumbnail_url()

  def get_url(self):
    return self.get_thumbnail_url()


class Level(models.Model):
  tower = models.ForeignKey(Tower, related_name='levels')
  level = models.IntegerField()
  question = models.TextField(verbose_name='문제', help_text='예) 입력으로 주어진 숫자의 factorial을 구하세요.')
  hint = models.TextField('힌트', help_text='3! = 3 * 2 * 1')

  def __unicode__(self):
    return u'%s %d층' % (self.tower.name, self.level)

  def message_size(self):
    return self.messages.count()

  def get_next_message_order(self):
    return self.message_size() + 1

class Case(models.Model):
  level = models.ForeignKey(Level, related_name='cases')
  input = models.TextField()
  output = models.TextField()

  def __unicode__(self):
    return u'%s %d층의 예제' % (self.level.tower.name, self.level.level)


class ClimbInfo(models.Model):
  tower = models.ForeignKey(Tower)
  user = models.ForeignKey(User, related_name='climb_infos')
  current_level = models.IntegerField(default=1)
  cleared = models.BooleanField(default=False)
  updated = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    if self.cleared:
      clear_msg = u'정복!'
    else:
      clear_msg = u'도전중.'
    return u'[%s] %s %d층 %s' % (self.user.first_name,
                                self.tower.name,
                                self.current_level,
                                clear_msg)

  class Meta:
    ordering = ['-updated']

class ClimbLevelInfo(models.Model):
  user = models.ForeignKey(User, related_name='climb_level_infos')
  level = models.ForeignKey(Level, related_name='climb_level_infos')
  current_case = models.ForeignKey(Case, blank=True, null=True)
  created = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    if self.current_case:
      return u'[%s] %s %d층의 예제' % (self.user.first_name,
                                      self.current_case.level.tower,
                                      self.current_case.level.level)
    else:
      return u'[%s] 예제 미지정' % self.user.first_name

  def set_random_case(self):
    # This function don't save the object, so you should save the object after
    # calling this function.
    if Case.objects.filter(level=self.level).exists():
      self.current_case = Case.objects.filter(level=self.level).order_by('?')[0]
    else:
      raise Http404('There is not enough cases.')

  def is_hint_allowed(self):
    return self.hint_opening_time() < datetime.now()

  def hint_opening_time(self):
    HINT_DELAY_SECOND = getattr(settings, 'HINT_DELAY_SECOND', 3600 * 24 * 3)
    return self.created + timedelta(seconds=HINT_DELAY_SECOND)


class Message(models.Model):
  level = models.ForeignKey(Level, related_name='messages')
  order = models.IntegerField()
  message = models.TextField(verbose_name='대화')
  action_image = models.ForeignKey(ActionImage, verbose_name='액션 이미지')

  def __unicode__(self):
    return u'[%s %d층] %s: %s' % (self.level.tower.name, self.level.level, self.action_image.guard.name, self.message)

  class Meta:
    ordering = ["level__level", "order"]
