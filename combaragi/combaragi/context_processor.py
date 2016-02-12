# -*- coding: utf-8 -*-
from community.models import UserProfile
from ccboard.models import Board

class BoardType:
  def __init__(self, slug, name):
    self.slug = slug
    self.name = name

  def is_new(self):
    return Board.objects.get(name=self.slug).is_new()

ALL_BOARDS = (
  BoardType('all', u'전체 게시글'),
  BoardType('notice', u'공지사항'),
  BoardType('freeboard', u'자유게시판'),
  BoardType('qna', u'질문/답변'),
  BoardType('subjects', u'과목'),
  BoardType('information', u'정보'),
  BoardType('photo', u'사진첩'),
)

def all_boards(request):
  return {
    'all_boards': ALL_BOARDS,
    'recent_members': UserProfile.objects.order_by('-recentActed')[:5],
  }
