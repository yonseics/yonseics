# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db import models
from django.db.models.query import QuerySet
from django.utils.html import escape
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from ccboard.models import Board
from django.core.exceptions import ObjectDoesNotExist     # 오브젝트가 없는 exception
from group.models import Group

from utils import get_portrait_path
from time import mktime

from mentoring.models import Question, Relation

from emblem import emblem_titles
from tower.models import Tower, ClimbInfo
from thumbs import ImageWithThumbsField


def get_tower_difficulty_color(difficulty):
  if difficulty == u'E':
    return 'green'
  elif difficulty == u'M':
    return 'orange'
  elif difficulty == u'H':
    return 'red'
  return 'purple'


def has_batchim(unichar):
  return (ord(unichar) - 44032) % 28


class EmblemTool():
  def __init__(self):
    self.emblem_titles = emblem_titles
    try:
      self.tower_emblem_count = Tower.objects.count()
      for tower in Tower.objects.all():
        color = get_tower_difficulty_color(tower.difficulty)
        if has_batchim(tower.name[-1]):
          connection_word = u'을'
        else:
          connection_word = u'를'
        self.emblem_titles[u'%s_cleared' % tower.slug] = {
            'title':u'%s%s 클리어한' % (tower.name, connection_word),
            'icon': 'check',
            'color': color,
            'checkFunc': lambda user, tower: (ClimbInfo.objects.filter(tower=tower, user=user).exists() and
                                              ClimbInfo.objects.get(tower=tower, user=user).cleared),
            'tower': tower
        }
    except:
      pass

  def emblem_sync(self):
    if self.tower_emblem_count != Tower.objects.count():
      self.__init__()
    if Emblem.objects.count() != len(self.emblem_titles):
      for title in self.emblem_titles:
        Emblem.objects.get_or_create(title=title)

  def is_obtainable(self, title, user):
    if self.tower_emblem_count != Tower.objects.count():
      self.__init__()
    if 'tower' in self.emblem_titles[title]:
      check_result = self.emblem_titles[title]['checkFunc'](user, self.emblem_titles[title]['tower'])
    else:
      check_result = self.emblem_titles[title]['checkFunc'](user)
    filtered_count = user.emblems.filter(title=title).count()
    return check_result and filtered_count == 0

  def obtain(self, title, user):
    Emblem.objects.get(title=title).user.add(user)

  def get_icon(self, title):
    if self.tower_emblem_count != Tower.objects.count():
      self.__init__()
    return u'<li style="color:%s;">%s</li>'%(
      self.emblem_titles[title]['color'],
      self.emblem_titles[title]['title'],
    )
emblem_tool = EmblemTool()

class Emblem(models.Model):
  user = models.ManyToManyField(User, related_name='emblems')
  title = models.CharField(unique=True, max_length=30)
  def __unicode__(self):
    return self.getName()
  def getName(self):
    return emblem_tool.emblem_titles[self.title]['title']
  def get_icon(self):
    return emblem_tool.get_icon(self.title)
  class Meta:
    ordering = ["title"]

#class EmblemRelation(models.Model):
#  user = models.ForeignKey(User)
#  Emblem = models.ForeignKey(Emblem)
#  available = models.BooleanField(default=False)  # 기본으로 false로 들어가고 유저가 승낙하면 true가 되어 사용가능

# Create your models here.
class UserProfile(models.Model):
  GENDER_CHOICES = (
    (u'M', u'남자'),
    (u'F', u'여자'),
  )
  STATUS_CHOICES = (
    (u'Y', u'재학생'),
    (u'G', u'대학원생'),
    (u'E', u'졸업생'),
  )
  NAME_INDEX_CHOICES = (
    (u'가', u'깋'),
    (u'나', u'닣'),
    (u'다', u'딯'),
    (u'라', u'맇'),
    (u'마', u'밓'),
    (u'바', u'빟'),
    (u'사', u'싷'),
    (u'아', u'잏'),
    (u'자', u'짛'),
    (u'차', u'칳'),
    (u'카', u'킿'),
    (u'타', u'팋'),
    (u'파', u'핗'),
    (u'하', u'힣'),
  )

  nameIndex = models.CharField(max_length=2, choices=NAME_INDEX_CHOICES)  # 성별. p.get_gender_display()로 쓰면 u'남' 이 나옵니다.
  user = models.ForeignKey(User, unique=True)
  currentEmblem = models.ForeignKey(Emblem, null=True, blank=True)      # 현재 엠블렘
  #nickname = models.CharField(max_length=20, unique=True)
  sid = models.CharField(max_length=10, unique=True, help_text='Student ID')  # 학번
  sidHash = models.CharField(max_length=44, unique=True)        # 학번의 해쉬값
  address = models.CharField(max_length=255, null=True, blank=True)        # 주소
  phone = models.CharField(max_length=15, null=True, blank=True)  # 전화번호
  gender = models.CharField(max_length=1, choices=GENDER_CHOICES)  # 성별. p.get_gender_display()로 쓰면 u'남' 이 나옵니다.
  status = models.CharField(max_length=1, choices=STATUS_CHOICES)    # 재학여부
  jobpos = models.CharField(max_length=50, blank=True, null=True)    # 연구실/직장
  sendmail = models.BooleanField()    # 메일수신 여부
  #pictureURL = models.URLField()      # 자기사진 URL
  #portrait = models.OneToOneField(Photo, null=True)  # 자기사진
  birthday = models.DateField(null=True, blank=True)
  portrait = ImageWithThumbsField(upload_to=get_portrait_path, blank=True, sizes=((64, 64), 300,))      # 자기사진
  homepageURL = models.URLField(blank=True)      # 홈페이지 URL
  #position = models.CharField(max_length=15, null=True, blank=True) # 네이버 맵 관련 자신의 위치
  visitCnt = models.IntegerField(default=0)
  bulletinCnt = models.IntegerField(default=0)    # 글쓴수
  commentCnt = models.IntegerField(default=0)      # 댓글 단 수
  #point = models.IntegerField(default=0)        # 포인트. 이거 그냥 aggregation사용하면 될 듯
  recentActed = models.DateTimeField(auto_now=True)  # 최근 이 사용자가 뭔가 한 시간
  introduction = models.TextField(blank=True)          # 자기소개
  knowns = models.ManyToManyField(User, related_name='my_knowns', blank=True)

  def get_point(self):
    return settings.POINT_BULLETIN * self.bulletinCnt + settings.POINT_COMMENT * self.commentCnt

  def get_pure_sid(self):
    sid = self.sid
    if len(sid) == 7:    # 06학번 이전
      return sid[0:2]
    elif len(sid) == 10:  # 07학번 이후
      return sid[2:4]

  def get_sn_color(self, sn):
    return '#%X' % ((967329 * int(sn) + 4199429) % 0xFFFFFF)    # 학번별로 고유한 색을 낼 수 있게 해줍니다.

  def get_email_front(self):
    return self.user.email.split('@')[0]
  def get_email_end(self):
    return self.user.email.split('@')[1]

  def get_my_full_name(self):    # 풀네임을 출력
    #memo_img = u''
    #mentoring_img = u''
    #if Memo.memos.filter(Q(to_user=self.user, read=False)).count():
    #  memo_img = memo_img + u'[메]'
    #if Memo.guestbooks.filter(Q(to_user=self.user, read=False)).count():
    #  memo_img = memo_img + u'[방]'
    # 자기 질문글이 답변이 달렸거나, 자기한테 질문이 올라왔거나.
    #if Question.objects.filter(Q(mentee=self.user, read=False)).exclude(reply=None).count():
    #  mentoring_img = mentoring_img + u'[답]'
    #if Question.objects.filter(Q(mentor__user=self.user, read=False, reply=None)).count():
    #  mentoring_img = mentoring_img + u'[질]'
    #if Relation.objects.filter(Q(mentor__user=self.user, accepted=False)).count():
    #  mentoring_img = mentoring_img + u'[멘]'
    emblem = ''
    if self.currentEmblem:
      emblem = u' rel="tooltip" title="%s"'%self.currentEmblem
    #return '<a%s href="/account/info/%s/"><font color="%s">%s</font> %s%s</a><a href="/mentoring/">%s</a>' % (emblem, self.sidHash, self.get_sn_color(self.get_pure_sid()), self.get_pure_sid(),escape(self.user.first_name), memo_img, mentoring_img)
    return '<a%s href="/account/info/%s/"><font color="%s">%s</font> %s</a>' % (emblem, self.sidHash, self.get_sn_color(self.get_pure_sid()), self.get_pure_sid(),escape(self.user.first_name))

  def get_portrait_url(self):
    if self.portrait:
      return self.portrait.url_300
    return settings.STATIC_URL + 'images/anonymous.jpg'

  def get_portrait_thumbnail(self):
    if self.portrait:
      return self.portrait.url_64x64
    return settings.STATIC_URL + 'images/avatar.jpg'

  def get_full_name_with_emblem(self):    # 풀네임을 출력
    if self.currentEmblem:
      return u'<a href="/account/info/%s/">%s <font color="%s">%s</font> %s</a>' % (self.sidHash, self.currentEmblem, self.get_sn_color(self.get_pure_sid()), self.get_pure_sid(),escape(self.user.first_name))
    return u'<a href="/account/info/%s/"><font color="%s">%s</font> %s</a>' % (self.sidHash, self.get_sn_color(self.get_pure_sid()), self.get_pure_sid(),escape(self.user.first_name))

  def get_full_name(self):    # 풀네임을 출력
    emblem = ''
    if self.currentEmblem:
      emblem = u' rel="tooltip" title="%s"'%self.currentEmblem
    return '<a%s href="/account/info/%s/"><font color="%s">%s</font> %s</a>' % (emblem, self.sidHash, self.get_sn_color(self.get_pure_sid()), self.get_pure_sid(),escape(self.user.first_name))

  def get_pure_full_name(self):    # 풀네임을 출력
    return '%s %s' % (self.get_pure_sid(), escape(self.user.first_name))

  def get_tval(self):
    return int(mktime(self.recentActed.timetuple()))

  def get_recent_feed_list(self):
    return self.user.feed_list.all()[0:3]

  def __unicode__(self):
#    return self.user.first_name     # 실명
    return self.get_full_name()      # 실명

  def check_mentoring(self):
    return Question.recents.filter(Q(mentee=self.user)|Q(mentor__user=self.user)).exists()
  def check_board(self, boardname):
    try:
      return Board.objects.get(name=boardname).is_new()
    except ObjectDoesNotExist:
      return False
  def check_group(self):
    return Group.objects.filter(Q(members=self.user) & Q(updated__gte=datetime.now()-timedelta(days=3))).exists()
  def check_notice(self):
    return self.check_board('notice')
  def check_freeboard(self):
    return self.check_board('freeboard')
  def check_subjects(self):
    return self.check_board('subjects')
  def check_photo(self):
    return self.check_board('photo')
  def check_intro(self):
    return self.check_board('self_introduction')
  def check_job(self):
    return self.check_board('job')
  def check_star(self):
    return self.check_board('star')
  def check_study(self):
    return self.check_board('study')
  def check_qna(self):
    return self.check_board('qna')
  def check_information(self):
    return self.check_board('information')
  def check_sid(self):
    return self.check_board(self.get_pure_sid())

class MemoManager(models.Manager):
  def get_query_set(self):
    return super(MemoManager, self).get_query_set().filter(secret=True)

class GuestBookManager(models.Manager):
  def get_query_set(self):
    return super(GuestBookManager, self).get_query_set().filter(secret=False)

class Memo(models.Model):
  from_user = models.ForeignKey(User, related_name='from')
  to_user = models.ForeignKey(User, related_name='to')
  content = models.TextField(null=False)      # 게시물 내용
  created = models.DateTimeField(auto_now_add=True)
  secret = models.BooleanField()
  read = models.BooleanField(default=False)
  objects = models.Manager()
  memos = MemoManager()
  guestbooks = GuestBookManager()

  class Meta:
    ordering = ["-created"]

  def __unicode__(self):
    return ' >> '.join([ self.from_user.first_name, self.to_user.first_name ])

class PointLog(models.Model):
  user = models.ForeignKey(User)
  year = models.PositiveSmallIntegerField()
  month = models.PositiveSmallIntegerField()
  point = models.IntegerField(default=0)

  class Meta:
    ordering = ["-point"]

  def __unicode__(self):
    return u'%s년 %s월 %s님의 포인트: %d점' % (self.year, self.month, self.user.first_name, self.point)

# Feed는 표시해 줄때
# 1. ~님이 당신의 방명록에 새 글을 남겼습니다.
# 2. ~님이 글에 댓글을 다셨습니다.
# 3. ~소모임에 ~님이 새 글을 남기셨습니다.
# 4. ~님이 새로운 쪽지를 보내셨습니다.
# 5. 멘티 ~님이 당신에게 새로운 질문을 요청하셨습니다.
# 6. 멘토 ~님이 당신의 질문에 답변을 올리셨습니다.
# 7. ~님이 당신을 지인으로 등록했습니다.
class Feed(models.Model):
  FEED_CHOICES = (
    (u'G', u'방명록'),
    (u'M', u'쪽지'),
    (u'C', u'댓글'),
    (u'N', u'공지사항'),
    (u'SM', u'스크랩글수정'),
    (u'SR', u'스크랩글댓글'),
    (u'MQ', u'멘토링질문'),
    (u'MR', u'멘토링답변'),
    (u'MI', u'멘토링요청'),
    (u'MA', u'멘토링수락'),
    #(u'K', u'지인등록'),
    (u'TN', u'이미지태그추가'),
    (u'TR', u'이미지태그삭제'),
    (u'IN', u'새이미지갤러리'),
    (u'GB', u'소모임글'),
    (u'GM', u'소모임글수정'),
    (u'GI', u'소모임초대'),
    (u'GE', u'소모임가입요청'),
    (u'GO', u'소모임회원승인'),
  )
  def get_message(self):
    if self.type == u'G':
      return u"%s님이 당신의 방명록에 <a href='/feed/go/%s/'>새 글</a>을 남겼습니다." % (self.from_user.get_profile().get_full_name(), self.id)
    if self.type == u'M':
      return u"%s님이 당신에게 <a href='/feed/go/%s/'>쪽지</a>를 보내셨습니다." % (self.from_user.get_profile().get_full_name(), self.id)
    if self.type == u'C':
      anomChar = self.additional[0]    # 익명성 보장
      if anomChar == '-': # 익명
        username = u'익명사용자'
      else:
        username = self.from_user.get_profile().get_full_name()
      return u"%s님이 <a rel='tooltip' title='%s' href='/feed/go/%s/'>댓글</a>을 남겼습니다." % (username, self.additional[1:], self.id)
    if self.type == u'N':
      return u"%s님이 <a rel='tooltip' title='%s' href='/feed/go/%s/'>새 공지사항</a>을 남기셨습니다." % (self.from_user.get_profile().get_full_name(), self.additional, self.id)
    if self.type == u'SM':
      anomChar = self.additional[0]    # 익명성 보장
      if anomChar == '-': # 익명
        username = u'익명사용자'
      else:
        username = self.from_user.get_profile().get_full_name()
      return u"당신이 <a rel='tooltip' title='%s' href='/feed/go/%s/'>좋아한 글</a>이 %s님에 의해 수정 되었습니다." % (self.additional[1:], self.id, username)
    if self.type == u'SR':
      anomChar = self.additional[0]    # 익명성 보장
      if anomChar == '-': # 익명
        username = u'익명사용자'
      else:
        username = self.from_user.get_profile().get_full_name()
      return u"당신이 <a rel='tooltip' title='%s' href='/feed/go/%s/'>좋아한 글</a>에 %s님이 <a rel='tooltip' title='%s' href='/feed/go/%s/'>댓글</a>을 다셨습니다." % (self.additional[1:], self.id, username, self.additional[1:], self.id)
    if self.type == u'MQ':
      return u"멘티 %s님이 당신에게 새로운 <a rel='tooltip' title='%s' href='/feed/go/%s/'>질문</a>을 요청하셨습니다." % (self.from_user.get_profile().get_full_name(), self.additional, self.id)
    if self.type == u'MR':
      return u"멘토 %s님이 당신의 질문에 <a rel='tooltip' title='%s' href='/feed/go/%s/'>답변</a>을 게시하였습니다." % (self.from_user.get_profile().get_full_name(), self.additional, self.id)
    if self.type == u'MI':
      return u"%s님이 당신에게 <a rel='tooltip' title='%s' href='/feed/go/%s/'>멘토요청</a>을 하였습니다." % (self.from_user.get_profile().get_full_name(), self.additional, self.id)
    if self.type == u'MA':
      return u"%s님이 당신의 멘토링 요청을 <a href='/feed/go/%s/'>수락</a> 하였습니다." % (self.from_user.get_profile().get_full_name(), self.id)
    if self.type == u'TN':
      return u"%s님이 <a rel='tooltip' title='%s' href='/feed/go/%s/'>태그</a>를 추가 하셨습니다." % (self.from_user.get_profile().get_full_name(), self.additional, self.id)
    if self.type == u'TR':
      return u"%s님이 <a rel='tooltip' title='%s' href='/feed/go/%s/'>태그</a>를 삭제 하셨습니다." % (self.from_user.get_profile().get_full_name(), self.additional, self.id)
    if self.type == u'IN':
      return u"새 <a rel='tooltip' title='%s' href='/feed/go/%s/'>갤러리</a>가 등록되었습니다." % (self.additional, self.id)
    if self.type == u'GB':
      return u"<a href='/group/%s/'>%s</a>에 <a href='/feed/go/%s/'>새글</a>을 게시하셨습니다." % (self.additional, Group.objects.get(id=self.additional).title, self.id)
    if self.type == u'GM':
      return u"<a href='/group/%s/'>%s</a>에 <a href='/feed/go/%s/'>글</a>이 수정되었습니다." % (self.additional, Group.objects.get(id=self.additional).title, self.id)
    if self.type == u'GI':
      return u"<a href='/feed/go/%s/'>%s</a>에서 당신을 <a href='/feed/go/%s/'>초대</a>하셨습니다." % (self.id, Group.objects.get(id=self.additional).title, self.id)
    if self.type == u'GE':
      return u"%s님이 <a href='/group/%s/'>%s</a>에 <a href='/feed/go/%s/'>가입신청</a>하셨습니다." % (self.from_user.get_profile().get_full_name(), self.additional, Group.objects.get(id=self.additional).title, self.id)
    if self.type == u'GO':
      return u"<a href='/feed/go/%s'>%s</a>에서 당신을 <a href='/feed/go/%s/'>등업</a>하였습니다." % (self.id, Group.objects.get(id=self.additional).title, self.id)
  url = models.URLField()      # feed return url
  from_user = models.ForeignKey(User, related_name='+')
  to_user = models.ForeignKey(User, related_name='feed_list')
  additional = models.CharField(max_length=20, null=True, blank=True)    # message
  type = models.CharField(max_length=2, choices=FEED_CHOICES)  # 성별. p.get_type_display()로 쓰면 상세정보가 나옵니다.
  created = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    #return u"%s <a id='feed_del_%s' href='#'><span class='btn_pack small icon'><span class='delete'></span><button type='button'>삭제</button></span></a>" % (self.get_message(), self.id)
    return self.get_message()

# 수상한 짓을 하는 사람들 정보를 저장해 놓는 곳
class BlackList(models.Model):
  user = models.ForeignKey(User, related_name='blacklist')
  desc = models.CharField(max_length=50)

class RegisterQuizActiveManager(models.Manager):
    def get_query_set(self):
        return QuerySet(self.model, using=self._db).filter(active=True)

class RegisterQuiz(models.Model):
    question = models.CharField(verbose_name='질문', max_length=100)
    answer = models.CharField(verbose_name='정답', max_length=100)
    active = models.BooleanField(default=True, verbose_name='활성화', help_text='활성화 되어 있어야 퀴즈가 나옵니다.')
    objects = models.Manager()
    actives = RegisterQuizActiveManager()

    def __unicode__(self):
        ret = u'%s: %s' % (self.question, self.answer)
        if not self.active:
            return u'[비활성화] - ' + ret
        return ret

class CurrentAdmin(models.Model):
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.user.first_name
