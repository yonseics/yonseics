# -*- coding: utf-8 -*-
# Author: UNKI
from django.contrib.auth.models import User
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from django.db.utils import DatabaseError
from mentoring.models import Mentor, Relation

__author__ = 'unki'

from ccboard.models import Bulletin, Scrap
from datetime import date, datetime

emblem_titles = {
    u'first_bulletin':{
      'title':u'가장 먼저 글을 작성한',
      'icon':'plus',
      'color':'red',
      'checkFunc':lambda user:
        (Bulletin.bulletIns.count() > 0 and
         Bulletin.bulletIns.all().order_by('created')[0].writer == user)
    },
    u'first_comment':{
      'title':u'가장 먼저 댓글을 작성한',
      'icon':'comment',
      'color':'red',
      'checkFunc':lambda user:
        (Bulletin.comments.count() > 0 and
         Bulletin.comments.all().order_by('created')[0].writer == user)
    },
    u'first_scrap':{
      'title':u'가장 먼저 스크랩한',
      'icon':'star',
      'color':'red',
      'checkFunc':lambda user:
        (Scrap.objects.count() > 0 and
         Scrap.objects.all().order_by('created')[0].user == user)
    },
    u'first_register':{
      'title':u'부지런한(가장 먼저 가입한)',
      'icon':'home',
      'color':'red',
      'checkFunc':lambda user: user.id == 1
    },
    u'2nd_register':{
      'title':u'2번째로 가입한',
      'icon':'home',
      'color':'red',
      'checkFunc':lambda user: user.id == 2
    },
    u'3rd_register':{
      'title':u'3번째로 가입한',
      'icon':'home',
      'color':'red',
      'checkFunc':lambda user: user.id == 3
    },
    u'4th_register':{
      'title':u'4번째로 가입한',
      'icon':'home',
      'color':'red',
      'checkFunc':lambda user: user.id == 4
    },
    u'5th_register':{
      'title':u'5번째로 가입한',
      'icon':'home',
      'color':'red',
      'checkFunc':lambda user: user.id == 5
    },
    u'fifty_register':{
      'title':u'50번째로 가입한',
      'icon':'home',
      'color':'pink',
      'checkFunc':lambda user: user.id == 50
    },
    u'hundred_register':{
      'title':u'100번째로 가입한',
      'icon':'home',
      'color':'blue',
      'checkFunc':lambda user: user.id == 100
    },
    u'two_hundred_register':{
      'title':u'200번째로 가입한',
      'icon':'home',
      'color':'teal',
      'checkFunc':lambda user: user.id == 100
    },
    u'first_bulletin_month':{
      'title':u'이번달에 먼저 글을 쓴',
      'icon':'plus',
      'color':'orange',
      'checkFunc':lambda user:
         (Bulletin.bulletIns.filter(updated__gte=date.today().replace(month=1, day=1)).count() > 0 and
          Bulletin.bulletIns.filter(updated__gte=date.today().replace(month=1, day=1)).order_by('created')[0].writer == user)
    },
    u'first_mentor':{
      'title':u'가장 처음 멘토가 된',
      'icon':'refresh',
      'color':'red',
      'checkFunc':lambda user:
        Mentor.objects.filter(user=user).exists() and user.mentor.id == 1
    },
    u'first_mentee':{
      'title':u'가장 처음 멘티가 된',
      'icon':'refresh',
      'color':'red',
      'checkFunc':lambda user:
        user.mentoring_relation.filter(id=1).exists()
    },
    u'point_winner_monthly':{
      'title':u'이번달 순위 1등을 해본',
      'icon':'dollar',
      'color':'orange',
      'checkFunc':lambda user:
        ((datetime.today().month == 2 and datetime.today().day > 25) or    # 2월은 26일 부터
         datetime.today().day > 27) and                    # 그외는 28일부터
        User.objects.filter(pointlog__month__exact=datetime.today().month).annotate(point=Sum('pointlog__point')) and
        User.objects.filter(pointlog__month__exact=datetime.today().month).annotate(point=Sum('pointlog__point')).order_by('-point')[0].id == user.id
    },
    u'point_winner_total':{
      'title':u'전체 순위 1등을 해본',
      'icon':'dollar',
      'color':'red',
      'checkFunc':lambda user:
        ((datetime.today().month == 2 and datetime.today().day > 25) or    # 2월은 26일 부터
         datetime.today().day > 27) and                    # 그외는 28일부터
        User.objects.annotate(point=Sum('pointlog__point')) and
        User.objects.annotate(point=Sum('pointlog__point')).order_by('-point')[0].id == user.id
    },
    # 점수가 후한(별방에 평점 만점을 100번 이상 준)
    # 점수가 박한(별방에 평점 0점을 100번 이상 준)
    # 자기소개를 한
    u'self_introduction':{
      'title':u'자기소개를 한',
      'icon':'rss',
      'color':'green',
      'checkFunc':lambda user:
        Bulletin.bulletIns.filter(
          Q(board__name='self_introduction')&Q(writer=user)).exists()
    },
    # 알려진(나를 지인으로 5명 이상 등록한)
    u'known':{
      'title':u'알려진(지인 5명 이상)',
      'icon':'person',
      'color':'green',
      'checkFunc':lambda user: user.my_knowns.count() >= 5
    },
    # 유명한(나를 지인으로 50명 이상 등록한)
    u'famous':{
      'title':u'유명한(지인 50명 이상)',
      'icon':'person',
      'color':'orange',
      'checkFunc':lambda user: user.my_knowns.count() >= 50
    },
    # 매우 유명한(나를 지인으로 100명 이상 등록한)
    u'very_famous':{
      'title':u'매우 유명한(지인 100명 이상)',
      'icon':'person',
      'color':'red',
      'checkFunc':lambda user: user.my_knowns.count() >= 100
    },
    # 모두가 아는(나를 지인으로 500명 이상 등록한)
    u'idol':{
      'title':u'모두가 아는(지인 500명 이상)',
      'icon':'person',
      'color':'purple',
      'checkFunc':lambda user: user.my_knowns.count() >= 100
    },
    # 수상한 짓을 해본
    u'hacking':{
      'title':u'수상한 짓을 해본',
      'icon':'cart',
      'color':'grey',
      'checkFunc':lambda user: user.blacklist.count() > 0
    },
    # 수상한 짓을 10번 이상 해본
    u'well_hacking':{
      'title':u'수상한 짓을 10번 이상 해본',
      'icon':'cart',
      'color':'black',
      'checkFunc':lambda user: user.blacklist.count() >= 10
    },
    # 글을 3개를 쓴
    u'3_bulletin':{
      'title':u'글을 3개 이상 쓴',
      'icon':'plus',
      'color':'green',
      'checkFunc':lambda user:
        (Bulletin.bulletIns.count() > 0 and
         Bulletin.bulletIns.filter(writer=user).count() >= 3)
    },
    # 글을 30개를 쓴
    u'30_bulletin':{
      'title':u'글을 30개 이상 쓴',
      'icon':'plus',
      'color':'orange',
      'checkFunc':lambda user:
        (Bulletin.bulletIns.count() > 0 and
         Bulletin.bulletIns.filter(writer=user).count() >= 30)
    },
    # 글을 300개를 쓴
    u'300_bulletin':{
      'title':u'글을 300개 이상 쓴',
      'icon':'plus',
      'color':'red',
      'checkFunc':lambda user:
        (Bulletin.bulletIns.count() > 0 and
         Bulletin.bulletIns.filter(writer=user).count() >= 300)
    },
    # 댓글을 10개를 쓴
    u'10_comment':{
      'title':u'댓글을 10개 이상 쓴',
      'icon':'comment',
      'color':'green',
      'checkFunc':lambda user:
        (Bulletin.bulletIns.count() > 0 and
         Bulletin.comments.filter(writer=user).count() >= 10)
    },
    # 댓글을 100개를 쓴
    u'100_comment':{
      'title':u'댓글을 100개 이상 쓴',
      'icon':'comment',
      'color':'orange',
      'checkFunc':lambda user:
        (Bulletin.bulletIns.count() > 0 and
         Bulletin.comments.filter(writer=user).count() >= 100)
    },
    # 댓글을 1000개를 쓴
    u'1000_comment':{
      'title':u'댓글을 1000개 이상 쓴',
      'icon':'comment',
      'color':'red',
      'checkFunc':lambda user:
        (Bulletin.bulletIns.count() > 0 and
         Bulletin.comments.filter(writer=user).count() >= 1000)
    },
  }

  # 일단 체크는...체크를 하고? 체크된 결과를 내보내 주는 것이 가장 나을 거 같다
  # 검사를 해서 만약 가능한 녀석이 있다면 그 해당 엠블렘이 유저를 포함하는지 검사하고 포함 하면 이미 등록된 엠블렘, 아니면 등록 안된 엠블렘이다.

