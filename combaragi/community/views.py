# -*- coding: utf-8 -*-
# Author: UNKI

from PIL import Image  # 아바타
from os import path    # 아바타

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Sum
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth import logout
from django.template import loader
from django.shortcuts import render_to_response
from django.template.defaultfilters import linebreaksbr
from ccboard.templatetags.linebreaksbrpre import linebreaksbrpre
from community.forms import AuthenticationForm, RegistrationForm, ModificationForm, GuestbookForm      # 여기 각종 폼 들이!
from community.models import UserProfile, Memo, Emblem, Feed
from community.rsa import gen_pubpriv_keys
from community.decorators import secure_required
from ccboard.models import Bulletin, RelatedFile
from django.contrib.auth.models import User       # 유저
from django.views.decorators.csrf import csrf_protect  # csrf보안을 위해
from django.views.decorators.cache import never_cache  # cache 안함
from django.views.decorators.cache import cache_page   # cache
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required   # 로그인 필수
from django.contrib.auth import REDIRECT_FIELD_NAME      # REDIRECT를 위해
#from django.contrib.auth.forms import AuthenticationForm   # 로그인 폼
import re
from datetime import date

from django.db.models import Q

from community.models import emblem_tool    # 엠블렘유틸
from community.emblem import emblem_titles

# 해시 함수 사용을 위해
from hashlib import md5
from hashlib import sha224
from base64 import b64encode

# 갤러리와 연동합니다.
from photologue.models import Gallery

from django.contrib.sites.models import RequestSite
from django.contrib.auth import login as auth_login
from django.core.exceptions import ObjectDoesNotExist     # 오브젝트가 없는 exception
from django.core import serializers

from combaragi import utils
from combaragi.community.models import CurrentAdmin
from combaragi.context_processor import ALL_BOARDS

from django.template import Context, loader

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context:
        user: requested user 
        all_boards: board list
    """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return HttpResponseServerError(t.render(Context({
        'user': request.user,
        'all_boards': ALL_BOARDS,
    })))


# 메인 페이지로 연결하는 메서드
@secure_required
def main_page(request, login_failed=False):
  #objects = Bulletin.bulletIns.all()[0:5]
  #return HttpResponse("공사중입니다.")
  # 공지사항 첫글을 보여주자.
  NOTICE_LENGTH_MAX = 27

  must_notice = None
  if Bulletin.bulletIns.filter(board__name='notice').exists():
    notice = Bulletin.bulletIns.filter(board__name='notice')[0]
    if Bulletin.bulletIns.filter(Q(board__name='notice') & Q(notice=True)).exists():
      must_notice = Bulletin.bulletIns.filter(Q(board__name='notice') & Q(notice=True))[0]
      if len(must_notice.title) > NOTICE_LENGTH_MAX:
        must_notice.title = '%s...' % must_notice.title[:NOTICE_LENGTH_MAX]
    else:
      must_notice = None
  else:
    notice = None
  
  birthdays = UserProfile.objects.filter(birthday__month=date.today().month)
  birthday_array = []
  for birthday in birthdays:
    birthday_array.append((birthday.birthday.day, birthday))
  birthday_array.sort()
  birthdays = [birthday_tuple[1] for birthday_tuple in birthday_array]
  birthday_left = map(lambda i: birthdays[i],filter(lambda i: i%2 == 0,range(len(birthdays))))
  birthday_right = map(lambda i: birthdays[i],filter(lambda i: i%2 == 1,range(len(birthdays))))

  current_admin = CurrentAdmin.objects.all()[0]

  is_mobile = 'HTTP_USER_AGENT' in request.META and any(device in request.META['HTTP_USER_AGENT'].lower() for device in ['iphone', 'android', 'ipad'])
  return direct_to_template(request, 'index.html', {        # parameter를 dictionary형식으로 넣을 수 있습니다.
    'notice':notice,
    'must_notice':must_notice,
    'next': request.GET.get('next', ''),
    'login_failed': login_failed,
    'birthday_left': birthday_left,
    'birthday_right': birthday_right,
    'is_mobile': is_mobile,
    'current_admin': current_admin
  })

# 장고에서 기본으로 제공하는 로그인 메서드를 그대로 가져옴
@csrf_protect
@never_cache
@secure_required
def login_page(request, template_name='account/login.html',
      redirect_field_name=REDIRECT_FIELD_NAME,
      authentication_form=AuthenticationForm):
  """Displays the login form and handles the login action."""

  redirect_to = request.REQUEST.get(redirect_field_name, '')

  if request.method == "POST":
    form = authentication_form(request.POST)
    if form.is_valid():
      # Light security check -- make sure redirect_to isn't garbage.
      if not redirect_to or ' ' in redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL

      # Heavier security check -- redirects to http://example.com should
      # not be allowed, but things like /view/?param=http://example.com
      # should be allowed. This regex checks if there is a '//' *before* a
      # question mark.
      elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
        redirect_to = settings.LOGIN_REDIRECT_URL

      # Okay, security checks complete. Log the user in.
      auth_login(request, form.get_user())

      if request.session.test_cookie_worked():
        request.session.delete_test_cookie()

      # 방문 횟수 1 증가
      profile = form.get_user().get_profile()
      profile.visitCnt += 1
      profile.save()
      next = request.GET.get('next', None)
      if next:
        return HttpResponseRedirect(next)
      return HttpResponseRedirect(redirect_to)

  request.session.set_test_cookie()

  return main_page(request, True)

# 로그아웃을 시켜주는 메서드
def logout_page(request):
  logout(request)              # 장고에서 기본적으로 제공하는 인증에서 로그아웃을 합니다.
  return HttpResponseRedirect('/')      # 메인페이지로 돌아갑니다.

# 등록 페이지를 열어주는 메서드
def register_page(request):
  PORTRAIT_WIDTH = 300
  if request.method == 'POST':
    form = RegistrationForm(qid=request.POST['question_type'], data=request.POST, files=request.FILES)
    if form.is_valid():
      user = User.objects.create_user(      # 여기서 유저 정보를 넣어 줍니다.
        username = form.cleaned_data['username'],
        password = form.cleaned_data['password1'],
        email = form.cleaned_data['email']
      )
      user.first_name = form.cleaned_data['realname']    # 유저 추가정보를 넣어 줍니다.
      if form.cleaned_data['sid'] == '0441003':
        user.is_staff = True
        user.is_superuser = True
      # 여기서 nameindex를 설정해 주자.
      name_index = u'가'
      first_char = user.first_name[0]
      for index in UserProfile.NAME_INDEX_CHOICES:
        if index[0] <= first_char and index[1] >= first_char:
          name_index = index[0]
          break
      form.cleaned_data['introduction'] = utils.stripXSS(
          form.cleaned_data['introduction'])    # Prevent XSS
      # if form.cleaned_data['portrait']:
      #   utils.resize_image(form.cleaned_data['portrait'].path, PORTRAIT_WIDTH)
      # 여기에 UserInfo라는 모델에 데이터를 넣는 부분을 추가합니다.
      # 기본 로그인은 User로 하되 추가적인 정보(학번이나 위치정보) 등은 UserInfo가 담고 있습니다.
      currentUserProfile = UserProfile.objects.create(user_id=user.id,
        sid=form.cleaned_data['sid'],        # 학번
        sidHash=md5(b64encode(sha224(form.cleaned_data['sid']).hexdigest())).hexdigest(),
        address=form.cleaned_data['address'],
        #nickname=form.cleaned_data['anomname'],
        phone=form.cleaned_data['phone'],
        nameIndex=name_index,
        gender=form.cleaned_data['gender'],
        status=form.cleaned_data['status'],
        jobpos=form.cleaned_data['jobpos'],
        sendmail=form.cleaned_data['sendmail'],
        homepageURL=form.cleaned_data['homepageURL'],
        birthday=form.cleaned_data['birthday'],
        #portrait=portrait,      # 초상화
        portrait=form.cleaned_data['portrait'],      # 초상화
        #pictureURL=form.cleaned_data['pictureURL'],
        #nametype=form.cleaned_data['nametype'],
        #position=form.cleaned_data['position'],
        introduction=form.cleaned_data['introduction'],
      )
      user.save()
      currentUserProfile.save()
      return HttpResponseRedirect(reverse('home')+'?next=/')
  else:
    form = RegistrationForm()

  return direct_to_template(request, 'account/register.html', {        # parameter를 dictionary형식으로 넣을 수 있습니다.
    'form': form
  })

# 회원정보를 수정하는 메서드
@login_required
def info_modify_page(request):
  try:
    currentUserProfile = request.user.get_profile()
  except ObjectDoesNotExist:
    currentUserProfile = UserProfile.objects.create(user=request.user)
  modificationMessage = ''    # 수정내용을 보여주는 메시지
  if request.method == 'POST':
    form = ModificationForm(request.POST, request.FILES)
    if form.is_valid():
      user = User.objects.get(username = request.user.username)  # 유저 정보를 가져옵니다.
      if form.cleaned_data['password1']:
        user.set_password(form.cleaned_data['password1'])  # 유저 추가정보를 넣어 줍니다.
      user.email = form.cleaned_data['email']        # 유저 추가정보를 넣어 줍니다.
      #user.first_name = form.cleaned_data['realname']    # 유저 추가정보를 넣어 줍니다.
      # 여기에 UserInfo라는 모델에서 데이터를 수정하는 부분을 추가합니다. 기본 로그인은 User로 하되 추가적인 정보(학번이나 위치정보) 등은 UserInfo가 담고 있습니다.
      form.cleaned_data['introduction'] = utils.stripXSS(form.cleaned_data['introduction'])    # Prevent XSS
      currentUserProfile.address = form.cleaned_data['address']
      currentUserProfile.phone = form.cleaned_data['phone']
      #currentUserProfile.gender = form.cleaned_data['gender']
      currentUserProfile.status = form.cleaned_data['status']
      currentUserProfile.jobpos = form.cleaned_data['jobpos']
      currentUserProfile.sendmail = form.cleaned_data['sendmail']
      currentUserProfile.homepageURL = form.cleaned_data['homepageURL']
      currentUserProfile.birthday = form.cleaned_data['birthday']
      if form.cleaned_data['portrait']:    # 초상화가 새로 들어온 경우만
        if currentUserProfile.portrait:      # 만약 기존 초상화가 있다면 지워준다.
          currentUserProfile.portrait.delete()
        currentUserProfile.portrait = form.cleaned_data['portrait']
        # utils.resize_image(form.cleaned_data['portrait'].path, PORTRAIT_WIDTH)
      #currentUserProfile.pictureURL = form.cleaned_data['pictureURL']
      #currentUserProfile.nametype = form.cleaned_data['nametype']
      #currentUserProfile.nickname = form.cleaned_data['anomname']    # 별명
      #currentUserProfile.position = form.cleaned_data['position']
      currentUserProfile.introduction = form.cleaned_data['introduction']
      user.save()              # 유저 정보 저장
      currentUserProfile.save()      # 저장해줌
      form = ModificationForm({      # 추가정보 변경
        'email':user.email,
        #'realname':user.first_name,
        #'anomname':currentUserProfile.nickname,
        #'gender':currentUserProfile.gender,
        'status':currentUserProfile.status,
        'jobpos':currentUserProfile.jobpos,
        'address':currentUserProfile.address,
        'phone':currentUserProfile.phone,
        'sendmail':currentUserProfile.sendmail,
        'homepageURL':currentUserProfile.homepageURL,
        'birthday':currentUserProfile.birthday,
        'portrait':currentUserProfile.portrait,
        #'pictureURL':currentUserProfile.pictureURL,
        #'nametype':currentUserProfile.nametype,
        #'position':currentUserProfile.position,
        'introduction':currentUserProfile.introduction,
        })
      request.user = user         # 유저정보 갱신
      modificationMessage = '수정되었습니다.'
  else:
    form = ModificationForm({
      'password1':'',
      'password2':'',
      'email':request.user.email,
      #'realname':request.user.first_name,
      #'anomname':currentUserProfile.nickname,
      #'gender':currentUserProfile.gender,
      'status':currentUserProfile.status,
      'jobpos':currentUserProfile.jobpos,
      'address':currentUserProfile.address,
      'phone':currentUserProfile.phone,
      'sendmail':currentUserProfile.sendmail,
      'homepageURL':currentUserProfile.homepageURL,
      'birthday':currentUserProfile.birthday,
      'portrait':currentUserProfile.portrait,
      #'pictureURL':currentUserProfile.pictureURL,
      #'nametype':currentUserProfile.nametype,
      #'position':currentUserProfile.position,
      'introduction':currentUserProfile.introduction,
      })

  return direct_to_template(request, 'account/modify.html', {        # parameter를 dictionary형식으로 넣을 수 있습니다.
    'form': form,
    'modificationMessage': modificationMessage,
  })

# 개인정보를 보여줍니다.
@login_required
def info_page(request, sidHash):
  if request.method == "POST":
    form = GuestbookForm(request.POST)
    if form.is_valid():
      if User.objects.filter(id=request.POST.get('to_user')).exists():
        Memo.guestbooks.create(
          from_user=request.user,
          to_user_id=request.POST.get('to_user'),
          content=form.cleaned_data['content'],
          secret=request.POST.get('secret')=='True',
        )
        target = User.objects.get(id=request.POST.get('to_user'))
        if target != request.user:
          if request.POST.get('secret')=='True':
            type='M'
          else:
            type='G'
          # 쪽지 혹은 방명록 Feed
          Feed.objects.create(
            url="/account/info/%s"%sidHash,
            from_user=request.user,
            to_user=target,
            additional=None,
            type=type,
          )
      return HttpResponseRedirect('/account/info/%s/' % sidHash)
  else:
    form = GuestbookForm()
  SAMPLE_SIZE = ":%s" % getattr(settings, 'GALLERY_SAMPLE_SIZE', 7)
  GALLERY_PAGENATED_SIZE = 7
  limit = request.GET.get('limit', 10)
  try:
    target = UserProfile.objects.get(sidHash=sidHash)
    target_user = target.user
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'target':'해당 유저가'})

  gallery_list = Gallery.objects.filter(owner=target_user)[:GALLERY_PAGENATED_SIZE]
  #for gallery in gallery_list:
  #  gallery.bulletin = Bulletin.objects.get(gallery=gallery)

  if target.user == request.user:
    memo_list = Memo.memos.filter(to_user=target_user)[:limit]      # 메모 목록
  else:
    memo_list = []

  guestbook_list = Memo.guestbooks.filter(to_user=target_user)[:limit]    # 방명록 목록

  # 유저가 로그인 하면 나한테 온 모든 안읽은 쪽지를 읽은 것으로 바꾼다
  if target_user == request.user:
    Memo.objects.filter(to_user=target_user).update(read=True)

  return direct_to_template(request, 'account/info.html', {        # parameter를 dictionary형식으로 넣을 수 있습니다.
    'target':target.user,
    'target_profile':target,
    'gallery_list':gallery_list,
    'is_paginated':len(gallery_list)>GALLERY_PAGENATED_SIZE,
    'hits':len(gallery_list),
    'sample_size':SAMPLE_SIZE,
    'memo_list':memo_list,
    'guestbook_list':guestbook_list,
    'form':form,
    'is_known':request.user.get_profile().knowns.filter(id=target.id).exists(),
  })

@login_required
@never_cache
def show_emblem(request):
  emblem_tool.emblem_sync()
  emblems = request.user.emblems
  availables = {}
  for titleid, title in emblem_titles.iteritems():
    if emblem_tool.is_obtainable(titleid, request.user):
      #availables[titleid] = title['title']
      availables[titleid] = emblem_tool.get_icon(titleid)
      #availaIbles.append(title)

  return direct_to_template(request, 'account/emblem.html', {        # parameter를 dictionary형식으로 넣을 수 있습니다.
    'availables':availables,
    #'taken':map(lambda a:{'id':a.id,'title':emblem_titles[a.title]['title']},emblems.all()),
    'taken':map(lambda a:{'id':a.id,'icon':a.get_icon()},emblems.all()),
  })

@login_required
def obtain_emblem(request, emblem_id):
  # 엠블렘을 obtain 가능한지 여부를 확인한다
  # 만약 obtain 가능하면 obtain하고 엠블렘 페이지로 redirect시킨다.
  if emblem_tool.is_obtainable(emblem_id, request.user):
    emblem_tool.obtain(emblem_id, request.user)
  else:
    if Emblem.objects.filter(title=emblem_id).count() > 0:
      return HttpResponseRedirect('/account/emblem/')
      #return render_to_response('noExist.html',{'user':request.user, 'target':u'해당 엠블렘(%s)을 가질 수'%
      #  Emblem.objects.get(title=emblem_id).getName()})
    else:
      return render_to_response('noExist.html',{'user':request.user, 'target':u'해당 엠블렘이'})
  return HttpResponseRedirect('/account/emblem/')

@login_required
def use_emblem(request, emblem_id):
  if Emblem.objects.get(id=emblem_id).user.filter(id=request.user.id).exists():    # 가지고 있는 엠블렘인가?
    user_profile = request.user.get_profile()
    user_profile.currentEmblem = Emblem.objects.get(id=emblem_id)
    user_profile.save()
  return HttpResponseRedirect('/account/emblem/')

@login_required
def show_known(request):
  return direct_to_template(request, 'account/known.html')

@login_required
def add_known(request, sidHash):
  try:
    uf = UserProfile.objects.get(sidHash=sidHash)
  except ObjectDoesNotExist:
    return HttpResponse("해당 유저가 없습니다.")
  target = uf.user
  curuf = request.user.get_profile()
  if curuf.knowns.filter(id=target.id).exists():
    return HttpResponse("이미 지인입니다.")
    #return render_to_response('noExist.html',{'user':request.user, 'target':u'이미 등록된 지인을 중복 등록할 수'})
  curuf.knowns.add(target)
  return HttpResponse("지인으로 등록 되었습니다.")
  #return HttpResponseRedirect('/account/info/%s/'%sidHash)

# TODO: 지인삭제 메뉴 만들기. URL에도 등록하기.
@login_required
def remove_known(request, kid):
  pass

@login_required
def go_feed_page(request, fid):
  try:
    feed = Feed.objects.get(id=fid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':u'해당 Feed가'})
  url = feed.url
  feed.delete()
  return HttpResponseRedirect(url)

@login_required
def del_feed_ajax(request, fid):
  try:
    feed = Feed.objects.get(id=fid)
  except ObjectDoesNotExist:
    return HttpResponse("해당 Feed가 없습니다.")
  feed.delete()
  return HttpResponse("Feed가 삭제 되었습니다.")

@login_required
def del_all_feed_ajax(request):
  request.user.feed_list.all().delete()
  return HttpResponse(u"<li>새로운 알림이 없습니다.</li>")

@login_required
def ranking_page(request):
  today = date.today()
  topN = getattr(settings, 'TOP_N', 7)
  MAX_SZ = getattr(settings, 'RANKING_MAX_SIZE', 400)
  total_top = User.objects.filter(is_staff=False).filter(pointlog__point__gte=0).annotate(point=Sum('pointlog__point')).order_by('-point')[:topN] # top 7
  monthly_top = User.objects.filter(is_staff=False).filter(pointlog__month__exact=today.month).annotate(point=Sum('pointlog__point')).order_by('-point')[:topN] # top 7
  if total_top:
    total_top1_point = total_top[0].point
  else:
    total_top1_point = 1
  if monthly_top:
    monthly_top1_point = monthly_top[0].point
  else:
    monthly_top1_point = 1
  for user in total_top:
    user.sz = float(user.point)/total_top1_point*MAX_SZ
  for user in monthly_top:
    user.sz = float(user.point)/monthly_top1_point*MAX_SZ
  return direct_to_template(request, 'account/ranking.html', {              # parameter를 dictionary형식으로 넣을 수 있습니다.
    'top10':{
      u'이번달 Top%d'%topN:monthly_top,
      u'전체 Top%d'%topN:total_top,
    },
    'my_monthly_point':User.objects.filter(Q(id=request.user.id)&Q(pointlog__month__exact=today.month)).aggregate(point=Sum('pointlog__point')),
    'my_total_point':User.objects.filter(id=request.user.id).aggregate(point=Sum('pointlog__point')),
  })

@login_required
def third_feed_ajax(request):
  feed_list = Feed.objects.filter(to_user=request.user)
  if len(feed_list) > 3:
    return HttpResponse(u'<li class="feed" id="feed_%s">%s <a id="feed_del_%s" href="#">삭제</a></li>'%(feed_list[2].id, feed_list[2].get_message(), feed_list[2].id))
  if len(feed_list) is 0:
    return HttpResponse(u"<li>새로운 알림이 없습니다.</li>")
  return HttpResponse("")

@login_required
def get_more_content_ajax(request, bid):
  # 현재 게시물이 뭔지 읽어온다.
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return HttpResponse("해당글이 없습니다.")

  if not bulletin.hasAuthToRead(request.user):
    return HttpResponse("해당글을 읽을 권한이 없습니다.")
  #return HttpResponse(linebreaksbrpre(bulletin.content))
  return direct_to_template(request, 'feeds/recent_content.html', {              # parameter를 dictionary형식으로 넣을 수 있습니다.
    'content': bulletin.content,
    'files': RelatedFile.objects.filter(bulletin=bulletin),
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def get_more_comments_ajax(request, bid, cnt):
  # 현재 게시물이 뭔지 읽어온다.
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return HttpResponse("해당글이 없습니다.")

  if not bulletin.hasAuthToRead(request.user):
    return HttpResponse("해당글을 읽을 권한이 없습니다.")

  return direct_to_template(request, 'feeds/recent_comments.html', {              # parameter를 dictionary형식으로 넣을 수 있습니다.
    'comment_list': bulletin.my_comments.all().order_by('created')[:cnt],
  })

@login_required
def get_recent_comments_ajax(request, bid, lcid):
  # 현재 게시물이 뭔지 읽어온다.
  try:
    bulletin = Bulletin.bulletIns.get(id=bid)
  except ObjectDoesNotExist:
    return HttpResponse("해당글이 없습니다.")

  if not bulletin.hasAuthToRead(request.user):
    return HttpResponse("해당글을 읽을 권한이 없습니다.")

  return direct_to_template(request, 'feeds/recent_comments.html', {              # parameter를 dictionary형식으로 넣을 수 있습니다.
    'comment_list': bulletin.my_comments.filter(id__gt=lcid).order_by('created'),
  })

@login_required
def get_more_feeds_ajax(request, page, board_name=None):
  howMany = 10
  NR_LIMIT = 10
  LENGTH_LIMIT = 50*NR_LIMIT
  page = int(page)
  if board_name:
    bulletins = Bulletin.bulletIns.filter(
      Q(deleted=False) &
      Q(board__secret=False) &
      Q(board__name=board_name)  # 학번게시판은 가져와 줘야지...
    ).order_by("-updated")[page*howMany:page*howMany+howMany]
  else:
    bulletins = Bulletin.bulletIns.filter(
      Q(deleted=False)&
      (Q(board__secret=False)
       |Q(board__name=request.user.get_profile().get_pure_sid())  # 학번게시판은 가져와 줘야지...
       |Q(board__group_board__members=request.user)# 소모임 게시판도 가져오고 싶은데...
      )
    ).order_by("-updated")[page*howMany:page*howMany+howMany]
  nrTag = re.compile(r"\n")
  #allTag = re.compile(r"<.+>")
  allTag = re.compile(r"<(/?\w+)( .+)?>")
  for bulletin in bulletins:
    # 더 보기를 만들어보자
    #if len(nrTag.findall(bulletin.content)) >= 2:
      #parted1 = bulletin.content.partition('\n')
      #parted2 = parted1[2].partition('\n')
      #bulletin.content = '%s'%'\n'.join([parted1[0], parted2[0]])
      #bulletin.truncated = True
    if len(nrTag.findall(bulletin.content)) >= NR_LIMIT:
      cnt = 0
      idx = 0
      for c in bulletin.content:
        if c == '\n':
          cnt += 1
        if cnt == NR_LIMIT:
          break
        idx += 1
      bulletin.content = bulletin.content[:idx]
      bulletin.truncated = True
    elif len(bulletin.content) > LENGTH_LIMIT:
      bulletin.content = '%s'%bulletin.content[:LENGTH_LIMIT]
      bulletin.truncated = True
    elif allTag.search(bulletin.content):
      bulletin.content = allTag.sub(ur'[이 글에는 \1태그가 포함되어 있습니다.]', bulletin.content)
      bulletin.truncated = True
    bulletin.remain_comment_cnt = bulletin.my_comments.count() - bulletin.get_recent_comments().count()
  #json_serializer.serialize(bulletins, ensure_ascii=False)
  #data = json_serializer.getvalue()
  #return HttpResponse(data)
  if not len(bulletins):
    return HttpResponse("")
  return direct_to_template(request, 'feeds/recent_feed.html', {              # parameter를 dictionary형식으로 넣을 수 있습니다.
    'bulletin_list': bulletins,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def account_list_page(request, iid=0):
  iid = int(iid)
  if iid >= len(UserProfile.NAME_INDEX_CHOICES) or iid < 0:
    return render_to_response('noExist.html',{'user':request.user, 'target':u'해당 인덱스가'})
  target_index = UserProfile.NAME_INDEX_CHOICES[iid][0]
  index_list = map(lambda a:{'name':a[0], 'count':UserProfile.objects.filter(nameIndex=a[0]).count()}, UserProfile.NAME_INDEX_CHOICES)


  return direct_to_template(request, 'account/list.html', {        # parameter를 dictionary형식으로 넣을 수 있습니다.
    'total_cnt':User.objects.count(),
    'index_list':index_list,
    'index_name':target_index,
    'user_list':User.objects.filter(userprofile__nameIndex=target_index).order_by('first_name')
  })

@login_required
def account_sid_list_page(request, sid):
  sid_int = int(sid)
  target_sid = sid
  if sid_int > 06 and sid_int < 82:
    target_sid = "20%s"%sid
  index_list = map(lambda a:{'name':a[0], 'count':UserProfile.objects.filter(nameIndex=a[0]).count()}, UserProfile.NAME_INDEX_CHOICES)

  return direct_to_template(request, 'account/list.html', {        # parameter를 dictionary형식으로 넣을 수 있습니다.
    'total_cnt':User.objects.count(),
    'index_list':index_list,
    'index_name':u'%s학번'%sid,
    'user_list':User.objects.filter(userprofile__sid__startswith=target_sid).order_by('first_name')
  })

@login_required
def avatar_img(request, uid):
  try:
    user = User.objects.get(id=uid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':u'해당 유저가'})
  uf = user.get_profile()
  response = HttpResponse(mimetype="image/png")
  if uf.portrait:
    image_path = user.get_profile().portrait.path
  else:
    image_path = "static/images/avatar.jpg"
  image = Image.open(image_path)
  ext = path.splitext(image_path)[1]  # extention만 빼냄
  if ext == '.jpg':    # jpg 면 jpeg로
    ext = '.jpeg'
  image.save(response, ext[1:])
  return response

# meta data를 보여줌.
@login_required
def meta_page(request):
  values = request.META.items()
  values.sort()
  html = []
  for k, v in values:
    html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
  return HttpResponse('<table>%s</table>' % '\n'.join(html))

# 로그인이 안되어 있으면 로그인 하라고 하는 wrapper method
def pre_login(view):
  def new_view(request, *args, **kwargs):
    if not request.user.is_authenticated():
      return HttpResponseRedirect('/login/')
    # TODO: 여기서 모든 로그인 후의 넘어가야 할 변수들이 넘어가는걸 할 수 있을까?
    return view(request, *args, **kwargs)
  return new_view

def error(request, message=None):
  return direct_to_template(request, 'error.html', {
    'message': message
  })
