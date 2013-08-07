# -*- coding: utf-8 -*-
# Author: UNKI

from django.db import models
from django.contrib.auth.models import User as Mentee
from tagging.fields import TagField
from tagging.models import Tag
from datetime import datetime, timedelta

"""
멘티와 멘토의 관계 (MM_Relation) - 당연한 말이지만 자기자신은 자기자신에게 멘토신청을 할 수 없다.
  멘토정보 (Mentor)
  멘티정보 (User)
  멘토의 수락여부 (boolean)
멘토 (Mentor)
  멘토의 유저정보(User)
  현재 자신이 가진 옥수수 알갱이 수 (Integer)
  재학여부 (boolean)
  현재 다니는 회사 (string)
  멘토링 가능한 분야 (TagModel, ManyToMany) (컴마로 연결해서 써 준다.)
멘티의 질문(Question)
  질문한 멘티(User)
  연계된 이전 질문(Question, Null일 수 있음)
  내가 질문하는 대상 멘토(정하지 않을 경우 자기 자신을 제외한 누구나 답변을 달 수 있음) (Mentor)
  질문 제목(string length=50)
  질문 내용(string)
  멘토의 답변 (한가지만 가능) (멘토의 답변이 달리면 질문은 삭제할 수 없다)
  답변한 멘토 (Mentor) 만약 내가 질문하는 대상멘토가 존재하고 그 사람과 이 멘토가 다르면 무결성 오류
  멘티의 답변 수락 여부. 추가질문을 할 때에는 자동으로 수락이 됨. (boolean)
  질문날짜 (date created)
  답변날짜 (date updated)
"""

class Mentor(models.Model):      # 멘토
  user = models.OneToOneField(Mentee, related_name='mentor')
  name = models.CharField(max_length=15)    # 멘토의 이름
  kernels = models.IntegerField(default=0)
  tags = TagField()    # 멘토의 상담가능 분야
  def set_tags(self, tags):
    Tag.objects.update_tags(self, tags)

  def get_tags(self, tags):
    return Tag.objects.get_for_object(self)

  def __unicode__(self):
    return self.user.first_name

class Relation(models.Model):  # 멘토와 멘티의 관계
  mentor = models.ForeignKey(Mentor)
  mentee = models.ForeignKey(Mentee, related_name='mentoring_relation')
  mentee_name = models.CharField(max_length=15)    # 멘티의 이름
  request_msg = models.CharField(max_length=100)    # 멘토요청 메시지
  accepted = models.BooleanField(default=False)
  def __unicode__(self):
#return " -> ".join([self.mentee.get_profile().get_pure_full_name(), self.mentor.user.get_profile().get_pure_full_name()])
    return self.mentor.user.get_profile().get_pure_full_name()

class RecentQuestionManager(models.Manager):
  def get_query_set(self):
    return super(RecentQuestionManager, self).get_query_set().filter(updated__gte=datetime.now()-timedelta(days=1))  # 현재 날짜로 하루전날까지 글의 수

class AllQuestionManager(models.Manager):
  def get_query_set(self):
    return super(AllQuestionManager, self).get_query_set()

class SolvedQuestionManager(models.Manager):
  def get_query_set(self):
    return super(SolvedQuestionManager, self).get_query_set().exclude(reply=None)

class UnsolvedQuestionManager(models.Manager):
  def get_query_set(self):
    return super(UnsolvedQuestionManager, self).get_query_set().filter(reply=None)

class Question(models.Model):    # 멘티의 질문
  mentee = models.ForeignKey(Mentee)
  parent = models.ForeignKey('self', null=True, blank=True)    # 현재 질문의 연관 질문
  mentor = models.ForeignKey(Mentor, related_name='to_mentor')
  title = models.CharField(max_length=50)
  content = models.TextField()
  reply = models.TextField(blank=True, null=True)
  read = models.BooleanField(default=False)
#  replyingMentor= models.ForeignKey(Mentor, null=True, blank=True, related_name='replying_mentor')
#  accepted = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add=True)  # 만들어진 날짜
  updated = models.DateTimeField(auto_now=True)    # 업데이트된 날짜
  objects = models.Manager()        # 주의! 반드시 기본 매니저를 가장 위에 써놓아야만 admin이 제대로 작동합니다.
  recents = RecentQuestionManager()    # 최근글
  alls = AllQuestionManager()        # 모든글
  solveds = SolvedQuestionManager()    # 해결된 글
  unsolveds = UnsolvedQuestionManager()  # 해결되지 않은 글
  def __unicode__(self):
    return ": ".join([self.mentee.first_name, self.title])

  class Meta:
    ordering = ["-created"]
