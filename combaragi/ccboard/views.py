# -*- coding: utf-8 -*-
# Author: UNKI

from itertools import chain

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.db.models import Q, Sum     # Q object
from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist     # 오브젝트가 없는 exception
from django.contrib.auth.decorators import login_required   # 로그인 필수
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from ccboard.models import Board, Bulletin, RelatedPosition, RelatedFile, PhotoTag, Category, Rate
from ccboard.forms import BulletinSearchForm, UserSearchForm, WriteAndModifyForm, CommentForm, AjaxCommentForm
from datetime import datetime
from community.models import PointLog, Feed

import utils

from re import search as re_search

from django.utils.html import strip_tags

from photologue.models import GalleryUpload, Photo
from ccboard.models import Scrap, Like

from utils import unique

# 기본 board의 속성.
basicBoards = {
    'notice':{'title':u'공지사항', 'desc':u'컴퓨터 과학과 전체의 공지사항을 담고있습니다.'},
    'freeboard':{'title':u'자유게시판', 'desc':u'자유롭게 하고싶은 말을 쓰시면 됩니다.'},
    'self_introduction':{'title':u'소개', 'desc':u'자신을 소개해 주시면 됩니다.'},
    #'study':{'title':u'학업/세미나', 'desc':u'함께 공부해요.'},
    #'job':{'title':u'취업/진로', 'desc':u'자신이 취업할 때 정리했던 것, 후배들에게 해주고 싶은 이야기를 남겨주세요.'},
    'photo':{'title':u'사진첩', 'desc':u'공유하고 싶은 사진을 올려요.'},
    'subjects':{'title':u'과목', 'desc':u'과목에 대하여 토론합시다.'},
    'qna':{'title':u'질문/답변', 'desc':u'자유롭게 질문을 올리는 공간입니다.'},
    'information':{'title':u'정보', 'desc':u'각종 정보를 올리는 공간입니다.'},
    #'guide':{'title':u'학교적응 가이드', 'desc':u'수강신청부터 필요한 것들을 담고 있습니다.'},
    #'papertree':{'title':u'족보게시판', 'desc':u'시험지 족보를 올려주세요. 교양, 전공 모두 환영합니다.'},
    #'book':{'title':u'추천도서', 'desc':u'프로그래머에게 필요하다 싶은 책은 추천해 주세요.'},
    #'hobby':{'title':u'취미공유', 'desc':u'취미를 공유해 봅시다.'},
    #'game':{'title':u'게임합시다', 'desc':u'컴과생에게 게임은 필수! 같이 게임해요~'},
    #'dronejava':{'title':u'드론자바', 'desc':u'역사깊은 스타크래프트 동아리. 드론자바.'},
    #'gongjava':{'title':u'공자바', 'desc':u'농구동아리 공자바'},
    #'gongchava':{'title':u'공차바', 'desc':u'축구동아리 공차바'},
    #'headhunting':{'title':u'병특/구인/구직', 'desc':u'직업을 구해봅시다.'},
    #'career':{'title':u'진로상담', 'desc':u'자신의 커리어에 대해 궁금한 것들에 대해 이야기 해 봅시다.'},
    #'another':{'title':u'타 전공 탐색', 'desc':u'다른 전공이 궁금하시다구요?'},
    #'highend':{'title':u'신기술 문의', 'desc':u'현재 최신의 가장 유행하는 기술은 어떤 것이 있을까요?'},
    #'contest':{'title':u'공모전', 'desc':u'이벤트를 위한 공모 게시판입니다.'},
    #'suggestion':{'title':u'건의/제안', 'desc':u'건의/제안을 하는 거니?'},
}

specialBoards = {
    'scrapbook':{'title':u'내 스크랩', 'desc':u'나의 스크랩북 입니다.', 'real':False},
    'likebook':{'title':u'내가 좋아한 글', 'desc':u'내가 좋아한 글들 입니다.', 'real':False},
    'my':{'title':u'내 글', 'desc':u'내가 작성한 글 목록 입니다.', 'real':False},
    'all':{'title':u'전체게시물', 'desc':u'전체 게시물 목록 입니다.', 'real':False},
    #'star':{'title':u'별방', 'desc':u'별점을 매겨봅시다.', 'real':True},
}

specialTemplate = [
  #'star',
  u'subjects',
  u'my',
]

categories = {
  'notice':[u'학과 공지', u'학생회 공지', u'세미나'],
  'freeboard':[u'잡담', u'개그', u'폭로', u'소식', u'자랑'],
  'photo':[u'MT', u'일상'],
  'self_introduction':[u'학부신입', u'대학원신입', u'재학생소개', u'회사소개'],
  #'job':[u'취업경험담', u'타전공탐색', u'구인/구직', u'유학'],
  #'study':[u'교재나눔', u'공부비법', u'세미나', u'질문'],
  'qna':[u'전공', u'타전공', u'취업', u'유학', u'수강신청', u'Abeek'],
  'information':[u'학교생활', u'취업', u'공부비법', u'대학원'],
}

# 학년, 과목이름
subjects = [
  (2, 2, u'인터넷프로그래밍'),
  (2, 2, u'자료구조/설계'),
  (2, 2, u'멀티미디어개론'),
  (2, 2, u'디지털논리회로/설계'),
  (2, 2, u'프로그래밍실습'),
  (3, 2, u'데이터베이스'),
  (3, 2, u'소프트웨어공학'),
  (3, 2, u'시스템프로그래밍'),
  (3, 2, u'오토메타형식언어'),
  (4, 3, u'소프트웨어종합설계'),
  (4, 2, u'인간과컴퓨터인터페이스'),
  (4, 2, u'인공지능'),
  (4, 2, u'정보보호'),
  (4, 2, u'게임프로그래밍'),
  (5, 1, u'채플'),
  (2, 1, u'객체지향프로그래밍'),
  (2, 1, u'컴퓨터시스템'),
  (5, 3, u'주니어세미나'),
  (2, 1, u'이산구조'),
  (2, 1, u'컴퓨터과학입문'),
  (3, 1, u'운영체제'),
  (3, 1, u'컴퓨터아키텍쳐'),
  (3, 1, u'프로그래밍언어구조론'),
  (3, 1, u'알고리즘분석'),
  (4, 1, u'컴파일러설계'),
  (4, 1, u'컴퓨터그래픽스'),
  (4, 1, u'컴퓨터네트워크'),
  (4, 1, u'모바일프로그래밍'),
  (1, 3, u'공학기초설계'),
  (1, 3, u'공학정보처리'),
  (5, 3, u'공학수학및기타수학과목'),
]
subjects.sort()

# 여기서 모든 보드를 그냥 만들어줄까...

def get_board(boardname):
  # 만약 보드이름이 숫자 두개로 구성되어 있다면 학번보드이다.
  if re_search("\d\d", boardname):
    board, created = Board.objects.get_or_create(name=boardname, title=u'%s학번' % boardname, desc=u'%s학번 게시판 입니다.' % boardname, secret=True)
    if created:
      for category in categories['freeboard']:
        Category.objects.create(board=board, title=category)  # 자유게시판과 동일한 카테고리
    return board
  if specialBoards.has_key(boardname):    # 만약 스페셜 보드인 경우
    boardInfo = specialBoards[boardname]  # 스페셜 보드에서 가져옴
    if boardInfo['real']:  # 진짜 보드인 경우 만들어줌
      return Board.objects.get_or_create(name=boardname, title=boardInfo['title'], desc=boardInfo['desc'])[0]
    else:          # 가짜인 경우 정보만 가져다 씀
      return Board(name=boardname, title=boardInfo['title'], desc=boardInfo['desc'])
  # 일반 board
  try:
    board = Board.objects.get(name=boardname)
  except ObjectDoesNotExist:
    if basicBoards.has_key(boardname):    # 기본 보드에 있는가? 있다면 만든다.
      boardInfo = basicBoards[boardname]
      board = Board.objects.create(name=boardname, title=boardInfo['title'], desc=boardInfo['desc'])
      if boardname == u'subjects':    # 과목게시판은 특별하다
        for subject in subjects:
          if subject[0] == 5:
            Category.objects.create(board=board, title=u'학년무관 - %s'%subject[2])
          elif subject[1] == 3:
            Category.objects.create(board=board, title=u'%d학년 1, 2학기 - %s'%(subject[0], subject[2]))
          else:
            Category.objects.create(board=board, title=u'%d학년 %d학기 - %s'%subject)
      else:
        if categories.has_key(boardname):
          for category in categories[boardname]:
            Category.objects.create(board=board, title=category)
    else:
      board = None
  return board

# 자동완성을 위한...
@login_required
def bulletin_ac(request, boardname):
  def iter_results(results):
    if results:
      for r in results:
        yield '%s\n' % r

  if not request.GET.get('q'):
    return HttpResponse(mimetype='text/plain')    # q가 없으면

  q = request.GET.get('q')
  limit = request.GET.get('limit', 15)
  try:
    limit = int(limit)
  except ValueError:
    return HttpResponseBadRequest()


  if boardname == 'scrapbook':
    target = Like.objects.filter(Q(isHiddenUser=False) & Q(user=request.user))
    acData = map(lambda b: b.bulletin.title, target.filter(bulletin__title__contains=q)[:limit])    # 타이틀 검색
    acData = acData + map(lambda b: b.bulletin.writer.first_name, target.filter(bulletin__writer__first_name__contains=q)[:limit])  # 글쓴 유저 검색
  elif boardname == 'my':
    target = Bulletin.bulletIns.filter(Q(isHiddenUser=False) & Q(writer=request.user))
    acData = map(lambda b: b.title, target.filter(title__contains=q)[:limit])    # 타이틀 검색
  else:
    board = Board.objects.get(name=boardname)
    target = Bulletin.bulletIns.filter(Q(isHiddenUser=False) & Q(board=board))
    acData = map(lambda b: b.title, target.filter(title__contains=q)[:limit])    # 타이틀 검색
    acData = acData + map(lambda b: b.writer.first_name, target.filter(writer__first_name__contains=q)[:limit])  # 글쓴 유저 검색
  acData = unique(acData)
  return HttpResponse(iter_results(acData), mimetype='text/plain')

#bulletin_ac = cache_page(bulletin_ac, 60 * 60)  # 캐쉬해 놓습니당.

# 자동완성을 위한...
@login_required
def user_ac(request):
  def iter_results(results):
    if results:
      for r in results:
        yield '%s %s\n' % (r.get_profile().get_pure_sid(), r.first_name)

  if not request.GET.get('q'):
    return HttpResponse(mimetype='text/plain')    # q가 없으면

  q = request.GET.get('q')
  limit = request.GET.get('limit', 10)
  try:
    limit = int(limit)
  except ValueError:
    return HttpResponseBadRequest()

  acData = User.objects.filter(first_name__contains=q)[:limit]

  return HttpResponse(iter_results(acData), mimetype='text/plain')

# user_ac = cache_page(user_ac, 60 * 60)  # 캐쉬해 놓습니당.

def main_page(request):
  return HttpResponseRedirect('freeboard')    # 자유게시판으로 가자

from itertools import islice, chain

class QuerySetChain(object):
  """
  Chains multiple subquerysets (possibly of different models) and behaves as
  one queryset.  Supports minimal methods needed for use with
  django.core.paginator.
  """

  def __init__(self, *subquerysets):
    self.querysets = subquerysets

  def count(self):
    """
    Performs a .count() for all subquerysets and returns the number of
    records as an integer.
    """
    return sum(qs.count() for qs in self.querysets)

  def _clone(self):
    "Returns a clone of this queryset chain"
    return self.__class__(*self.querysets)

  def _all(self):
    "Iterates records in all subquerysets"
    return chain(*self.querysets)

  def __getitem__(self, ndx):
    """
    Retrieves an item or slice from the chained set of results from all
    subquerysets.
    """
    if type(ndx) is slice:
      return list(islice(self._all(), ndx.start, ndx.stop, ndx.step or 1))
    else:
      return islice(self._all(), ndx, ndx+1).next()


@login_required
def list_page(request, boardname):
  if re_search("\d\d", boardname) and int(boardname) != int(request.user.get_profile().get_pure_sid()):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 게시판에 접근할 권한이'})

  page = int(request.GET.get('page', 1))
  bulletinPerPage = getattr(settings, 'BULLETIN_PER_PAGE', 15)  # 한 페이지에 표시하는 게시물 수
  board = get_board(boardname)

  if board is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'게시판이'})

  try:
    if not board.group_board.members.filter(id=request.user.id).exists():
      return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임게시판에 접근할 권한이'})
  except ObjectDoesNotExist:
    pass

  if boardname == 'likebook':
    supportWrite = False    # 글쓰기를 지원하는가
    like_list = Like.objects.filter(Q(user=request.user) & Q(bulletin__deleted=False))
    total_bulletin = like_list.count()
    like_list = like_list[bulletinPerPage * (page - 1):bulletinPerPage * page]
    bulletinList = [like.bulletin for like in like_list]
    bulletinCount = len(bulletinList)
  elif boardname == 'my':  # 내가 쓴 글
    supportWrite = False
    list = Bulletin.bulletIns.filter(Q(writer=request.user) &
                                     Q(deleted=False))  # 총 리스트
    total_bulletin = list.count()  # 총 카운트
    bulletinList = list[bulletinPerPage*(page-1):bulletinPerPage*page]
    bulletinCount = bulletinList.count()
  elif boardname == 'all':  # 전체 게시물
    supportWrite = False
    key = request.GET.get('key', None)
    list = Bulletin.bulletIns.filter(
      Q(deleted=False) &
      (Q(board__secret=False)
       |Q(board__group_board__members=request.user)# 소모임 게시판도 가져오고 싶은데...
       |Q(board__name=request.user.get_profile().get_pure_sid())  # 학번게시판은 가져와 줘야지...
      )
    )  # 총 리스트
    if key:
      list = list.filter(
        Q(isHiddenUser=False) &
        (Q(title__icontains=key) |
         Q(writer__first_name__icontains=key)
        )
      )
    total_bulletin = list.count()  # 총 카운트
    bulletinList = list[bulletinPerPage*(page-1):bulletinPerPage*page]
    bulletinCount = bulletinList.count()
  else:
    supportWrite = True    # 글쓰기를 지원한다
    # 여기서 리스트를 받아온다.
    list = Bulletin.bulletIns.filter(Q(board=board) &
                                     Q(notice=False) &
                                     Q(deleted=False))  # 총 리스트
    total_bulletin = list.count()  # 총 카운트
    list = list[bulletinPerPage*(page-1):bulletinPerPage*page]

    bulletinCount = list.count()
    if page is 1:
      noticeList = Bulletin.notices.filter(Q(board=board) & Q(deleted=False))
      bulletinList = QuerySetChain(noticeList, list)
    else:
      bulletinList = list

  form = BulletinSearchForm(boardname=boardname, data=request.GET)
  if (page is not 1) and len(bulletinList) is 0:
    return HttpResponseRedirect('/board/%s/' % boardname)    # 기본 페이지에 가자


  total_page = total_bulletin / bulletinPerPage    # 총 페이지
  if total_bulletin % bulletinPerPage:  # 남는게 있으면
    total_page += 1             # 갯수 하나 늘려줌
  no_seq = total_bulletin - (page-1) * bulletinPerPage - bulletinCount    # 번호 시퀀스!
  page_before = page-5         # 이전 다섯 페이지
  page_after = page+5         # 다음 다섯 페이지
  sPage = max(1, page-4)          # 페이지 시작
  ePage = min(page+4, total_page) + 1   # 페이지 끝
  page_list = range(sPage, ePage)      # 페이지 리스트

  if boardname in specialTemplate:
    template_name = 'board/list_content/%s_list.html' % boardname
  else:
    template_name = 'board/list_content/base_list.html'
  return direct_to_template(request, template_name, {
    'form':form,        # 검색폼. 테스트용.
    'supportWrite':supportWrite,  # 지원하는 것
    'board':board,        # 게시판 아이디
    'page':page,        # 현재 페이지
    'no_seq':no_seq,      # 현재 index seq start number
    'total_page':total_page,  # 총 페이지
    'page_before':page_before,  # 이전 5장
    'page_after':page_after,  # 다음 5장
    'page_list':page_list,    # 페이지 리스트
    'bulletinList':bulletinList,    # 게시물 리스트
  })

@login_required
def write_page(request, boardname):
  if re_search("\d\d", boardname) and int(boardname) != int(request.user.get_profile().get_pure_sid()):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 게시판에 접근할 권한이'})
  board = get_board(boardname)
  try:
    if not board.group_board.members.filter(id=request.user.id).exists():
      return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임게시판에 접근할 권한이'})
  except ObjectDoesNotExist:
    pass
  if board is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'게시판이'})
  if request.method == 'POST':
    form = WriteAndModifyForm(data=request.POST, files=request.FILES, board=board)
    if form.is_valid():
      form.cleaned_data['content'] = utils.stripXSS(form.cleaned_data['content'])     # Prevent XSS
      form.cleaned_data['content'] = utils.CompleteHTML(form.cleaned_data['content']) # complete HTML
      bulletin = Bulletin.bulletIns.create(
        writer=request.user,              # 글쓴이
        #writerIP=request.META['REMOTE_ADDR'][-7:],    # 아이피는 뒤에 일곱자리만 저장합니다.
        writerIP=request.META['REMOTE_ADDR'],      # 아이피를 전부 저장합니다.
        isHiddenUser = form.cleaned_data['nametype'],  # 익명 유저 여부
        board=Board.objects.get(name=boardname),    # 보드이름
        title=form.cleaned_data['title'],        # 제목
        content=form.cleaned_data['content'],      # 내용
        #secret=form.cleaned_data['secret'],
        notice=form.cleaned_data['notice'],
        #category=form.cleaned_data['category'],
      )        # 비밀여부
      if form.cleaned_data['position']:    # 위치정보가 있을 경우
        RelatedPosition.objects.create(
          bulletin=bulletin,
          title=form.cleaned_data['positionTitle'],
          position=form.cleaned_data['position'],
        )
      if form.cleaned_data['file']:  # 파일
        for file in form.cleaned_data['file']:
          RelatedFile.objects.create(
            board=board,
            bulletin=bulletin,
            file=file,
            size=file.size,
          )
      if len(bulletin.title) > 20:
        additionalTitle = '%s...' % bulletin.title[:17]
      else:
        additionalTitle = bulletin.title[:20]
      if form.cleaned_data['gallery'] and board.name == "photo":    # 갤러리가 있을 경우
        # 갤러리를 만들고 거기 올린다.
        bulletin.gallery = GalleryUpload(owner=request.user,
            zip_file=form.cleaned_data['gallery'],
            title=' >> '.join([board.title, form.cleaned_data['title']]),
            #is_public=not form.cleaned_data['gallery_is_not_public']).save()
            is_public=True).save()
        bulletin.save()    # 저장
        # 전체 유저에게 Feed 추가
        for user in User.objects.all():
          if bulletin.writer != user:
            Feed.objects.create(
              url="/board/%s/read/%s/"%(boardname, bulletin.id),
              from_user=bulletin.writer,
              to_user=user,
              additional=additionalTitle,
              type=u'IN',
            )
      # 글 작성시 사용자가 작성한 글이 하나 올라감
      plusPoint(request, bulletin)
      # 공지사항일 경우 모든 사용자에게 Feed를 달아준다.
      if boardname == 'notice':
        for user in User.objects.all():
          if request.user != user:
            Feed.objects.create(
              url="/board/%s/read/%s/"%(boardname, bulletin.id),
              from_user=request.user,
              to_user=user,
              additional=additionalTitle,
              type=u'N',
            )
      try:
        if board.group_board:
          # 소모임의 모든 사람들에게 Feed를 달아준다
          for user in board.group_board.members.all():
            if user != request.user:
              Feed.objects.create(
                url="/board/%s/read/%s/"%(boardname, bulletin.id),
                from_user=request.user,
                to_user=user,
                additional=board.group_board.id,
                type=u'GB',
              )
          # 소모임 상태를 갱신해준다(new)
          board.group_board.save()
      except ObjectDoesNotExist:
        pass
      board.save()  # 보드 상태도 갱신
      return HttpResponseRedirect(reverse('board-list', args=[boardname]))
  else:
    form = WriteAndModifyForm(board=board)

  tpl = loader.get_template('board/write_and_modify.html')    # write.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'board':board,
    'form':form,
    'type':'write',
    'typeText':u'작성',
    'boardname':boardname,
    'MAX_A_FILE_SIZE':settings.MAX_A_FILE_SIZE,
    'MAX_TOTAL_FILE_SIZE':settings.MAX_TOTAL_FILE_SIZE,
    })
  return HttpResponse(tpl.render(ctx))

@login_required
def modify_page(request, boardname, bid):
  if re_search("\d\d", boardname) and int(boardname) != int(request.user.get_profile().get_pure_sid()):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 게시판에 접근할 권한이'})
  board = get_board(boardname)
  try:
    if not board.group_board.members.filter(id=request.user.id).exists():
      return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임게시판에 접근할 권한이'})
  except ObjectDoesNotExist:
    pass
  if board is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'게시판이'})
  page = int(request.GET.get('page', 1))
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당글이'})

  if not bulletin.isMyBulletin(request.user):    # 내 글이 아니라면...
    return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))
  if bulletin.deleted:
    return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))

  # 그리고 수정가능한 시각인지 확인해야 한다. 글쓴지 일주일이상 지났으면 수정이 불가능.
  if (datetime.now() - bulletin.created).days >= settings.CAN_MODIFY_DAYS:
    # 일주일이상 지난 것
    return HttpResponseRedirect('/board/%s/read/%s/?page=%d' % (boardname, int(bid), page))
  try:
    relatedPosition = RelatedPosition.objects.get(bulletin=bulletin)
  except ObjectDoesNotExist:
    relatedPosition = None
  if request.method == 'POST':
    form = WriteAndModifyForm(data=request.POST, files=request.FILES, board=board)
    if form.is_valid():    # 폼이 옳다면
      form.cleaned_data['content'] = utils.stripXSS(form.cleaned_data['content'])    # Prevent XSS
      form.cleaned_data['content'] = utils.CompleteHTML(form.cleaned_data['content']) # complete HTML
      #if form.cleaned_data['nametype'] == u'실명':
      #if form.cleaned_data['nametype'] == False:
      #  bulletin.isHiddenUser = False    # 익명 여부를 FALSE로
      #else:
      #  bulletin.isHiddenUser=True       # 익명 여부를 TRUE로
      bulletin.isHiddenUser=form.cleaned_data['nametype']
      bulletin.title=form.cleaned_data['title']
      bulletin.content=form.cleaned_data['content']
      #bulletin.secret=form.cleaned_data['secret']
      bulletin.notice=form.cleaned_data['notice']
      bulletin.save()
      if form.cleaned_data['position']:
        if relatedPosition:      # 이미 있다면 그냥 바꾸고 저장
          relatedPosition.title=form.cleaned_data['positionTitle']
          relatedPosition.position=form.cleaned_data['position']
          relatedPosition.save()
        else:            # 없다면 새로 만듦.
          RelatedPosition.objects.create(
            bulletin=bulletin,
            title=form.cleaned_data['positionTitle'],
            position=form.cleaned_data['position'],
          )
      else:      # 만약 포지션이 삭제 되었는데...
        if relatedPosition:        # 등록된 것이 있다면
          relatedPosition.delete()  # 가차없이 삭제
      if form.cleaned_data['file']:  # 파일
        for file in form.cleaned_data['file']:
          RelatedFile.objects.create(
            board=board,
            bulletin=bulletin,
            file=file,
            size=file.size,
          )
      if form.cleaned_data['gallery'] and board.name == "photo":    # 갤러리가 있을 경우
        if bulletin.gallery:        # 이미 있으면 삭제
          for photo in bulletin.gallery.photos.all():
            photo.delete()
          bulletin.gallery.delete()    # 여기 안에 사진 다 삭제해야 함..ㅠ
        # 갤러리를 만들고 거기 올린다.
        bulletin.gallery = GalleryUpload(owner=request.user,
            zip_file=form.cleaned_data['gallery'],
            title=' >> '.join([board.title, form.cleaned_data['title']]),
            #title=form.cleaned_data['title'],
            is_public=True).save()
        bulletin.save()    # 저장
      if boardname == 'star':
        if Rate.objects.filter(bulletin=bulletin).exists(): # 있다면
          rate = Rate.objects.get(bulletin=bulletin)
          rate.rate = form.cleaned_data['starpoint'],
          rate.save()
        else:
          Rate.objects.create(
            rate = form.cleaned_data['starpoint'],
            bulletin = bulletin
          )
      # 익명이면 - 아니면 +를 달아준다.
      if bulletin.isHiddenUser:
        anomChar = '-'
      else:
        anomChar = '+'
      # 스크랩한 모든 사람들에게 Feed를 달아준다
      for like in bulletin.likes.all():
        user = like.user
        if user != request.user:
          if len(bulletin.title) > 20:
            additionalTitle = '%s...' % bulletin.title[:17]
          else:
            additionalTitle = bulletin.title[:20]
          Feed.objects.create(
            url="/board/%s/read/%d/?page=%d"%(boardname, int(bid), page),
            from_user=request.user,
            to_user=user,
            additional='%s%s'%(anomChar, additionalTitle),
            type=u'SM',
          )
      try:
        if board.group_board:
          # 소모임의 모든 사람들에게 Feed를 달아준다
          for user in board.group_board.members.all():
            if user != request.user:
              Feed.objects.create(
                url="/board/%s/read/%s/"%(boardname, bid),
                from_user=request.user,
                to_user=user,
                additional=board.group_board.id,
                type=u'GM',
              )
          # 소모임 상태를 갱신해준다(new)
          board.group_board.save()
      except ObjectDoesNotExist:
        pass
      board.save()  # 보드 상태도 갱신
      return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))
  else:
    if relatedPosition:    # 좌표 있으면
      rTitle = relatedPosition.title
      rPos = relatedPosition.position
    else:      # 좌표 없으면
      rTitle = ''
      rPos = ''

    form = WriteAndModifyForm(board=board, data={
        'title':bulletin.title,
        'content':bulletin.content,
        'positionTitle':rTitle,
        'position':rPos,
        'nametype':bulletin.isHiddenUser,
        'notice':bulletin.notice,
        #'secret':bulletin.secret,
        })
  relatedFile = RelatedFile.objects.filter(bulletin=bulletin)
  for file in relatedFile:
    file.name = file.file.name.split('/')[-1]

  tpl = loader.get_template('board/write_and_modify.html')    # write.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'board':board,
    'bulletin':bulletin,
    'form':form,
    'page':page,
    'type':'modify',
    'typeText':u'수정',
    'files':relatedFile,
    'boardname':boardname,
    'MAX_A_FILE_SIZE':settings.MAX_A_FILE_SIZE,
    'MAX_TOTAL_FILE_SIZE':settings.MAX_TOTAL_FILE_SIZE,
    })
  return HttpResponse(tpl.render(ctx))

@login_required
def read_page(request, boardname, bid):
  if re_search("\d\d", boardname) and int(boardname) != int(request.user.get_profile().get_pure_sid()):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 게시판에 접근할 권한이'})
  board = get_board(boardname)

  try:
    if not board.group_board.members.filter(id=request.user.id).exists():
      return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임게시판에 접근할 권한이'})
  except ObjectDoesNotExist:
    pass

  if board is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'게시판이'})
  page = int(request.GET.get('page', 1))    # 페이지

  modify_days = settings.CAN_MODIFY_DAYS

  if "gotoIndex" in request.GET:
    gotoIndex = request.GET["gotoIndex"]
    if not int(gotoIndex):
      gotoIndex = ""
  else:
    gotoIndex = ""

  # 현재 게시물이 뭔지 읽어온다.
  try:
    bulletin = Bulletin.objects.get(id=bid)
    #bulletin.hits += 1       # 조회수를 1 올린다.
    #bulletin.save()
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당글이'})  # 해당글이 없으면 없다는 것으로!

  if request.method == 'POST' and not bulletin.deleted:
    form = CommentForm(data=request.POST, board=board, bulletin=bulletin, user=request.user)
    if form.is_valid():
      form.cleaned_data['content'] = utils.stripXSS(form.cleaned_data['content'])    # Prevent XSS
      form.cleaned_data['content'] = utils.CompleteHTML(form.cleaned_data['content']) # complete HTML
      # 코멘트 작성
      # 기존 댓글에 덧글 수 하나 올려준다
      bulletin.commentCnt += 1
      bulletin.save()
      comment = Bulletin.comments.create(
        rate = form.cleaned_data['starpoint'],
        writer=request.user,
        parent=bulletin,
        #writerIP=request.META['REMOTE_ADDR'][-7:],    # 아이피는 뒤에 일곱자리만 저장합니다.
        writerIP=request.META['REMOTE_ADDR'],      # 아이피를 전부 저장합니다.
        isHiddenUser = form.cleaned_data['nametype'],        # 익명 여부 저장
        board=bulletin.board,    # 보드
        title='comment',                # 제목
        content=form.cleaned_data['content'],      # 내용
        #secret=form.cleaned_data['secret'])        # 비밀여부
        secret=False)
      # 코멘트 작성은 포인트 settings.POINT_COMMENT점
      plusPoint(request, comment)
      #Rate.objects.create(
      #  rate = form.cleaned_data['starpoint'],
      #  bulletin = comment
      #)
      # 익명이면 - 아니면 +를 달아준다.
      '''
      if comment.isHiddenUser:
        anomChar = '-'
      else:
        anomChar = '+'

      striped_content = strip_tags(comment.content)
      if len(striped_content) > 19:
        sum_content = '%s...'%striped_content[0:16]
      else:
        sum_content = striped_content[0:19]
      # Feed를 달아준다.
      if bulletin.writer != comment.writer:
        Feed.objects.create(
          url="/board/%s/read/%d/?page=%d&to=%s"%(boardname, int(bid), page, comment.id),
          from_user=request.user,
          to_user=bulletin.writer,
          additional='%s%s'%(anomChar, sum_content),
          type=u'C',
        )
      distinct_comment_user = map(lambda a:User.objects.get(id=a), set(map(lambda a:a['writer'], bulletin.my_comments.values("writer"))))
      for comment_user in distinct_comment_user:
        if comment_user != comment.writer and comment_user != bulletin.writer:
          Feed.objects.create(
            url="/board/%s/read/%d/?page=%d&to=%s"%(boardname, int(bid), page, comment.id),
            from_user=request.user,
            to_user=comment_user,
            additional='%s%s'%(anomChar, sum_content),
            type=u'C',
          )
      # 스크랩한 모든 사람들에게 Feed를 달아준다
      if not comment.secret:
        for like in bulletin.likes.all():
          user = like.user
          url="/board/%s/read/%d/?to=%s"%(boardname, int(bid), comment.id)
          if user != request.user and not Feed.objects.filter(Q(url=url)&Q(to_user=user)).exists():
            Feed.objects.create(
              url=url,
              from_user=request.user,
              to_user=user,
              additional='%s%s'%(anomChar, sum_content),
              type=u'SR',
            )
      '''
      try:
        if board.group_board:
          # 소모임 상태를 갱신해준다(new)
          board.group_board.save()
      except ObjectDoesNotExist:
        pass
      bulletin.save()    # 글 상태도 갱신해준다.
#      board.save()  # 보드 상태도 갱신  2015/01/06 it slows down comment.
      return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))
  else:
    form = CommentForm(board=board, bulletin=bulletin, user=request.user)

  if not bulletin.hasAuthToRead(request.user):
    bulletin.title = u'권한이 없습니다.'
    bulletin.content = u'권한이 없습니다.'
    bulletin.canRead = False
    commentList = []
  else:
    commentList = Bulletin.comments.filter(parent=bulletin).order_by('created')

  # 만약 삭제되었다면, title과 content를 삭제하여 내보내 준다.
  if bulletin.deleted:
    bulletin.title='삭제된 글입니다.'
    bulletin.content='삭제된 글입니다.'


  if bulletin.gallery and (board.name == "photo" or board.name == "all"):
    bulletin.photos = bulletin.gallery.public()
    for photo in bulletin.photos:
      photo.tags = PhotoTag.objects.filter(photo=photo)

  for comment in commentList:
    #isRated = comment.isMyComment
    if not comment.hasAuthToRead(request.user):
      #comment.writer = None
      comment.title = u'권한이 없습니다.'
      comment.content = u'권한이 없습니다.'
    comment.can_modify = not((datetime.now() - comment.created).days >= modify_days)
    comment.is_my_comment = comment.isMyComment(request.user)

  isRated = False
  rateOrder = 1
  rate = 0
  rate_writer = 1

  # 익명으로 달린 댓글들 처리
  commentHiddenUserList = []
  commentHiddenUserNumber = 1
  for comment in commentList:
    if comment.isHiddenUser:
      if comment.writer == bulletin.writer and bulletin.isHiddenUser:
          comment.hiddenUser = "글쓴이"
      else:
        if comment.writer in commentHiddenUserList:
          comment.hiddenUser = "익명%d" % (commentHiddenUserList.index(comment.writer) + 1)
        else:
          commentHiddenUserList.append(comment.writer)
          comment.hiddenUser = "익명%d" % commentHiddenUserNumber
          commentHiddenUserNumber += 1


  try:
    relatedPosition = RelatedPosition.objects.get(bulletin=bulletin)
  except ObjectDoesNotExist:
    relatedPosition = None

  relatedFile = RelatedFile.objects.filter(bulletin=bulletin)
  image_files = []
  other_files = []
  for file in relatedFile:
    file.name = file.file.name.split('/')[-1]
    if file.isImage():
      image_files.append(file)
    else:
      other_files.append(file)

  can_modify = not((datetime.now() - bulletin.created).days >= modify_days)
  tpl = loader.get_template('board/read.html')    # read.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'form':form,
    'board':board,
    'bulletin':bulletin,
    'can_modify':can_modify,
    'modify_days':modify_days,
    'page':page,
    'naver_map_key':settings.NAVER_MAP_KEY,
    'scraped':Scrap.objects.filter(user=request.user, bulletin=bulletin).exists(),  # 자신이 스크랩 하였는가?
    'liked':Like.objects.filter(user=request.user, bulletin=bulletin).exists(),  # 자신이 좋아 하였는가?
    'like_list':Like.objects.filter(bulletin=bulletin),
    'scraps':Scrap.objects.filter(bulletin=bulletin),    # 이 글의 스크랩들
    'gotoIndex':gotoIndex,
    'commentList':commentList,
    'isMyBulletin':bulletin.isMyBulletin(request.user),
    'relatedPosition':relatedPosition,    # 연관 위치
    'files':other_files,
    'image_files':image_files,
    'boardname':boardname,
    'rate':rate,
    'isRated':isRated,
    'rateNumber':rateOrder-1,
    'rate_writer':rate_writer,
    'toComment':request.GET.get('to', 0)
    })
  return HttpResponse(tpl.render(ctx))

@login_required
def scrap_ajax(request, bid):
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return render_to_response('noexist.html',{'user':request.user, 'target':'해당글이'})
  if bulletin.deleted:
    return render_to_response('noexist.html',{'user':request.user, 'target':'해당글이'})
  scrap, created = Scrap.objects.get_or_create(user=request.user, bulletin=bulletin)
  if created:  # create가 true라면 잘 만들어진 것임
    return HttpResponse("스크랩 되었습니다.")
  return HttpResponse("이미 스크랩 되었습니다.")

@login_required
def like_ajax(request, bid):
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당글이'})
  if bulletin.deleted:
    return render_to_response('noexist.html',{'user':request.user, 'target':'해당글이'})
  like, created = Like.objects.get_or_create(user=request.user, bulletin=bulletin)
  if created:  # create가 true라면 잘 만들어진 것임
    return HttpResponse("당신이 이글을 좋아합니다.")
  return HttpResponse("이미 좋아합니다.")

@login_required
def comment_append_ajax(request, bid):
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당글이'})
  board = bulletin.board
  boardname = board.name
  if request.method == "POST":
    form = AjaxCommentForm(request.POST)
    if form.is_valid():
      content = utils.stripXSS(form.cleaned_data['content'])
      content = utils.CompleteHTML(content) # complete HTML
      # 코멘트 작성
      comment = Bulletin.comments.create(
        rate = 0,
        writer=request.user,
        parent=bulletin,
        #writerIP=request.META['REMOTE_ADDR'][-7:],    # 아이피는 뒤에 일곱자리만 저장합니다.
        writerIP=request.META['REMOTE_ADDR'],      # 아이피를 전부 저장합니다.
        isHiddenUser = False,        # 익명 여부 저장
        board=bulletin.board,    # 보드
        title='ajax_comment',                # 제목
        content=content,      # 내용
        #secret=form.cleaned_data['secret'])        # 비밀여부
        secret=False)
      # 코멘트 작성은 포인트 settings.POINT_COMMENT점
      plusPoint(request, comment)
      # 익명이면 - 아니면 +를 달아준다.
      if comment.isHiddenUser:
        anomChar = '-'
      else:
        anomChar = '+'

      striped_content = strip_tags(comment.content)
      if len(striped_content) > 19:
        sum_content = '%s...'%striped_content[0:16]
      else:
        sum_content = striped_content[0:19]
      # Feed를 달아준다.
      if bulletin.writer != comment.writer:
        Feed.objects.create(
          url="/board/%s/read/%d/?to=%s"%(boardname, int(bid), comment.id),
          from_user=request.user,
          to_user=bulletin.writer,
          additional='%s%s'%(anomChar, sum_content),
          type=u'C',
        )
      distinct_comment_user = map(lambda a:User.objects.get(id=a), set(map(lambda a:a['writer'], bulletin.my_comments.values("writer"))))
      for comment_user in distinct_comment_user:
        if comment_user != comment.writer and comment_user != bulletin.writer:
          Feed.objects.create(
            url="/board/%s/read/%d/?to=%s"%(boardname, int(bid), comment.id),
            from_user=request.user,
            to_user=comment_user,
            additional='%s%s'%(anomChar, sum_content),
            type=u'C',
          )
      # 스크랩한 모든 사람들에게 Feed를 달아준다
      if not comment.secret:
        for like in bulletin.likes.all():
          user = like.user
          url="/board/%s/read/%d/?to=%s"%(boardname, int(bid), comment.id)
          if user != request.user and not Feed.objects.filter(Q(url=url)&Q(to_user=user)).exists():
            Feed.objects.create(
              url=url,
              from_user=request.user,
              to_user=user,
              additional='%s%s'%(anomChar, sum_content),
              type=u'SR',
            )
      try:
        if board.group_board:
          # 소모임 상태를 갱신해준다(new)
          board.group_board.save()
      except ObjectDoesNotExist:
        pass
      # 기존 댓글에 덧글 수 하나 올려준다
      bulletin.commentCnt += 1
      bulletin.save()  # 글 상태도 갱신해준다.
      board.save()  # 보드 상태도 갱신
    return HttpResponse("성공")
  return HttpResponse("실패")

@login_required
def comment_delete_ajax(request, cid):
  try:
    comment = Bulletin.comments.get(id=cid)
  except ObjectDoesNotExist:
    return HttpResponse("글없음 실패")
  if comment.writer == request.user:
    comment.parent.commentCnt -= 1
    comment.parent.save()
    comment.delete()
    return HttpResponse("성공")
  return HttpResponse("유저다름 실패")

@login_required
def delete_page(request, boardname, bid):
  if re_search("\d\d", boardname) and int(boardname) != int(request.user.get_profile().get_pure_sid()):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 게시판에 접근할 권한이'})
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당글이'})
  page = int(request.GET.get('page', 1))
  # 이미 삭제된 글이면 걍 넘어갑니다. *수상한놈*
  if bulletin.deleted:
    return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))

  can_delete = not((datetime.now() - bulletin.created).days >= settings.CAN_MODIFY_DAYS)
  if can_delete and bulletin.isMyBulletin(request.user):
    # bulletin.delete()    # 여기서 게시물을 삭제한다.
    #실제로 삭제하는 것이 아니라 삭제 플래그만 달아준다.
    bulletin.deleted = True
    # 관련 position과 gallery와 파일을 삭제한다.
    try:
      relatedPosition = RelatedPosition.objects.get(bulletin=bulletin)
    except ObjectDoesNotExist:
      relatedPosition = None
    if relatedPosition:
      relatedPosition.delete()
    if bulletin.gallery:        # 이미 있으면 삭제
      # 이건 특이한 케이스이기 때문에...
      photos_list = bulletin.gallery.photos.all()
      for photo in photos_list:
        photo.delete()
      bulletin.gallery.delete()    # 여기 안에 사진 다 삭제해야 함..ㅠ
      bulletin.gallery = None
    for file in RelatedFile.objects.filter(bulletin=bulletin): # 파일도 다 삭제해 줍시다
      file.delete()

    bulletin.save()
    # 글 삭제는 포인트 POINT_BULLETIN 만큼 차감.
    reducePoint(request, bulletin)
    return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))
  else:
    # 삭제를 못하는 경우이다.
    return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))

@login_required
def delete_comment_page(request, boardname, bid, cid):
  if re_search("\d\d", boardname) and int(boardname) != int(request.user.get_profile().get_pure_sid()):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 게시판에 접근할 권한이'})
  page = int(request.GET.get('page', 1))
  try:
    comment = Bulletin.comments.get(id=cid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 코멘트가'})
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당글이'})

  can_delete = not((datetime.now() - comment.created).days >= settings.CAN_MODIFY_DAYS)
  if can_delete and comment.isMyBulletin(request.user):
    # 코멘트 삭제는 포인트 POINT_COMMENT만큼 차감.
    reducePoint(request, comment)
    comment.delete()    # 여기서 댓글을 삭제한다.
    bulletin.commentCnt -= 1
    bulletin.save()
    return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))
  else:
    # 삭제를 못하는 경우이다.
    return HttpResponseRedirect('/board/%s/read/%d/?page=%d'% (boardname, int(bid), page))

# 이건 수정 페이지에서 이루어 집니다.
@login_required
def delete_file_page(request, boardname, fid):
  if re_search("\d\d", boardname) and int(boardname) != int(request.user.get_profile().get_pure_sid()):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 게시판에 접근할 권한이'})
  page = int(request.GET.get('page', 1))
  try:
    file = RelatedFile.objects.get(id=fid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당파일이'})
  bulletin = file.bulletin
  bid = bulletin.id

  can_delete = not((datetime.now() - bulletin.created).days >= settings.CAN_MODIFY_DAYS)
  if can_delete and bulletin.isMyBulletin(request.user):
    file.delete()    # 여기서 파일을 삭제한다.
    return HttpResponseRedirect('/board/%s/modify/%d/?page=%d'% (boardname, int(bid), page))
  else:
    # 삭제를 못하는 경우이다.
    return HttpResponseRedirect('/board/%s/modify/%d/?page=%d'% (boardname, int(bid), page))

# 이건 수정 페이지에서 이루어 집니다.
@login_required
def add_tag_page(request, boardname, bid, pid, pidx):
  if re_search("\d\d", boardname) and int(boardname) != int(request.user.get_profile().get_pure_sid()):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 게시판에 접근할 권한이'})
  board = get_board(boardname)
  try:
    if not board.group_board.members.filter(id=request.user.id).exists():
      return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임게시판에 접근할 권한이'})
  except ObjectDoesNotExist:
    pass
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return render_to_response('noexist.html',{'user':request.user, 'target':'해당글이'})
  try:
    photo = Photo.objects.get(id=pid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당사진이'})
  page = request.GET.get('page', 1)

  if request.method == 'POST':
    key = request.POST["key"]
    if key:
      x = request.POST["x"]
      y = request.POST["y"]
      w = request.POST["w"]
      h = request.POST["h"]
      if x != '-' and y != '-' and w != '-' and h != '-':
        PhotoTag.objects.create(photo=photo,
            title=key,
            x=x,
            y=y,
            w=w,
            h=h,
            )
        # Feed 추가
        if bulletin.writer != request.user:
          Feed.objects.create(
            url="/board/%s/read/%d/"%(boardname, int(bid)),
            from_user=request.user,
            to_user=bulletin.writer,
            additional=key[:20],
            type=u'TN',
          )
        return HttpResponse("<script>opener.window.location.href='/board/%s/read/%d/?page=%d&gotoIndex=%d';/*opener.window.location.reload(true);*/ self.close();</script>" % (boardname, int(bid), int(page), int(pidx)-1))
  userSearchForm = UserSearchForm(request.GET)
  tpl = loader.get_template('board/addTag.html')    # addTag.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'userSearchForm':userSearchForm,
    'photo':photo,
    })
  return HttpResponse(tpl.render(ctx))

@login_required
def delete_tag_page_ajax(request, tid):
  try:
    photoTag = PhotoTag.objects.get(id=tid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당태그가'})
  # Feed 추가
  bulletin = photoTag.photo.galleries.all()[0].bulletin
  if bulletin.writer != request.user:
    Feed.objects.create(
      url="/board/%s/read/%s/"%(bulletin.board.name, bulletin.id),
      from_user=request.user,
      to_user=bulletin.writer,
      additional=photoTag.title[:20],
      type=u'TR',
    )
  photoTag.delete()    # 여기서 태그를 삭제한다.
  return HttpResponse("")

@login_required
def notice_out_ajax(request, bid):
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return HttpResponse(u"해당글이 없습니다.")
  if bulletin.notice:
    bulletin.notice = False
    bulletin.save()
    return HttpResponse(u"정상적으로 공지에서 내려갔습니다.")
  return HttpResponse("")

@login_required
def notice_in_ajax(request, bid):
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return HttpResponse(u"해당글이 없습니다.")
  if not bulletin.notice:
    bulletin.notice = True
    bulletin.save()
    return HttpResponse(u"정상적으로 공지로 올라갔습니다.")
  return HttpResponse("")

@login_required
def direct_read(request, bid):
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당글이'})
  return HttpResponseRedirect("/board/%s/read/%s/"%(bulletin.board.name, bulletin.id))


# 포인트 변경
def changePoint(request, bulletin, changeValue):
  currentUserProfile = request.user.get_profile()
  pointLog = PointLog.objects.get_or_create(user=request.user, year=datetime.now().year, month=datetime.now().month)
  pointLog = pointLog[0]
  if isBulletin(bulletin):
    currentUserProfile.bulletinCnt = currentUserProfile.bulletinCnt + changeValue
    pointLog.point = pointLog.point + settings.POINT_BULLETIN*changeValue    # 해당 포인트 만큼 더해줌
  else:
    currentUserProfile.commentCnt = currentUserProfile.commentCnt + changeValue
    pointLog.point = pointLog.point + settings.POINT_COMMENT*changeValue    # 해당 포인트 만큼 더해줌
  pointLog.save()    # 저장한다
  currentUserProfile.save()  # 역시 저장

# 포인트 추가
def plusPoint(request, bulletin):
  changePoint(request, bulletin, 1)
# 포인트 감소
def reducePoint(request, bulletin):
  changePoint(request, bulletin, -1)
def isBulletin(bulletin):
  return bulletin.parent is None

def scrap_book_page(request):
  return list_page(request, "scrapbook")
def like_book_page(request):
  return list_page(request, "likebook")

def all_page(request):
  tpl = loader.get_template('board/all.html')      # all.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'board_list': Board.objects.filter(secret=False).order_by('title'),
    })
  return HttpResponse(tpl.render(ctx))

