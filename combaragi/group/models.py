# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from ccboard.models import Board, Bulletin

class Group(models.Model):
  owner = models.ForeignKey(User, related_name='my_groups')
  members = models.ManyToManyField(User, related_name='member_groups')
  semi_members = models.ManyToManyField(User, related_name='+')
  name = models.CharField(max_length=20, unique=True)    # 영문이름
  title = models.CharField(max_length=30, unique=True)  # 그냥 이름
  desc = models.TextField()    # 그룹 설명
  board = models.OneToOneField(Board, related_name='group_board')
  hidden = models.BooleanField(default=False)  # 비공개일 경우 어디에도 그룹이 보이지 않는다. 비공개 그룹의 그룹장은 다른 사람을 초대할 수 있다.
  updated = models.DateTimeField(auto_now=True, auto_now_add=True)

  def __unicode__(self):
    return self.title

  def is_new(self):
    #return Bulletin.objects.filter(Q(board=self.board) & Q(updated__gte=datetime.now()-timedelta(days=1))).exists()
    return self.board.is_new()

