# -*- coding: utf-8 -*-
# Author: UNKI

from django.conf import settings
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User       # 유저
from community.models import UserProfile, Feed
from group.models import Group
from ccboard.models import Board, Category
from group.forms import CreateGroupForm, ManageGroupForm, InviteGroupForm
from django.core.exceptions import ObjectDoesNotExist     # 오브젝트가 없는 exception

from utils import stripXSS    # XSS공격 방지
from utils import checkCSRF_with_tval, dealCSRF

# 해시 함수 사용을 위해
from hashlib import md5
from hashlib import sha224
from base64 import b64encode

# 자동완성을 위한...
def autocomplete(request):
  def iter_results(results):
    if results:
      for r in results:
        yield '%s\n' % (r.first_name)

  if not request.GET.get('q'):
    return HttpResponse(mimetype='text/plain')    # q가 없으면

  q = request.GET.get('q')
  limit = request.GET.get('limit', 15)
  try:
    limit = int(limit)
  except ValueError:
    return HttpResponseBadRequest()

  names = User.objects.filter(first_name__contains=q)[:limit]

  return HttpResponse(iter_results(names), mimetype='text/plain')

@login_required
def main_page(request):
  tpl = loader.get_template('group/main.html')    # write.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'group_list':Group.objects.filter(hidden=False),
    'my_group_list':request.user.member_groups.all(),
  })
  return HttpResponse(tpl.render(ctx))

# 그룹의 메인 페이지
@login_required
def group_main_page(request, gid):
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})

  tpl = loader.get_template('group/info.html')    # write.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    "current_group":group,
    'is_member':group.members.filter(id=request.user.id).exists(),
    'is_semi_member':group.semi_members.filter(id=request.user.id).exists(),
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def create_page(request):
  if request.method == "POST":
    form = CreateGroupForm(request.POST)
    if form.is_valid():
      #form.cleaned_data['desc'] = stripXSS(form.cleaned_data['desc'])    # Prevent XSS
      board = Board.objects.create(
        name=form.cleaned_data['name'],
        title=form.cleaned_data['title'],
        secret=True,
        desc=form.cleaned_data['desc']
      )
      group = Group.objects.create(
        owner=request.user,
        name=form.cleaned_data['name'],
        title=form.cleaned_data['title'],
        desc=form.cleaned_data['desc'],
        board=board,
        hidden=form.cleaned_data['hidden'],
      )
      group.members.add(request.user)
      return HttpResponseRedirect('/group/')
  else:
    form = CreateGroupForm()
  tpl = loader.get_template('group/create.html')    # create.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    "form":form,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def enter_page(request, gid):
  if checkCSRF_with_tval(request):
    return dealCSRF(request)
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if group.hidden and not group.members.filter(id=request.user.id).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임에 접근할 권한이'})
  if group.semi_members.filter(id=request.user.id).exists() or group.members.filter(id=request.user.id).exists():
    return HttpResponse("이미 가입 되었거나 가입신청 대기중입니다.")
  group.semi_members.add(request.user)
  Feed.objects.create(
    url="/group/%s/manage/"%group.id,
    from_user=request.user,
    to_user=group.owner,
    additional=group.id,
    type=u'GE',
  )
  return HttpResponse("가입 요청이 처리 되었습니다. 승인을 기다려 주세요.")

@login_required
def leave_page(request, gid):
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if group.hidden and not group.members.filter(id=request.user.id).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임에 접근할 권한이'})

  tpl = loader.get_template('.html')    # leave.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    "current_group":group,
    'is_member':group.members.filter(id=request.user.id).exists(),
    'is_semi_member':group.semi_members.filter(id=request.user.id).exists(),
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def manage_page(request, gid):
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if group.hidden and not group.members.filter(id=request.user.id).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임에 접근할 권한이'})
  if group.owner != request.user:
    return render_to_response('noExist.html',{'user':request.user, 'target':'관리자가 아닙니다. 권한이'})

  if request.method == "POST":
    form = ManageGroupForm(group=group, data=request.POST)
    if form.is_valid():
      #group.desc = stripXSS(form.cleaned_data['desc'])    # Prevent XSS
      group.desc = form.cleaned_data['desc']
      group.title = form.cleaned_data['title']
      group.hidden = form.cleaned_data['hidden']
      group.save()  # 그룹 저장
      group.board.title = form.cleaned_data['title']
      # TODO(limsungkee): Data truncated error 떠서 일단은 보드 설명은 업데이트 안되게 해 놓었습니다.
      #group.board.desc = form.cleaned_data['desc']
      group.board.save()
      for user in form.cleaned_data['semi_members']:    # 가입승인
        group.semi_members.remove(user)
        group.members.add(user)
        Feed.objects.create(
          url="/group/%s/"%group.id,
          from_user=request.user,
          to_user=user,
          additional=group.id,
          type=u'GO',
        )
      if form.cleaned_data['added_category']:
        Category.objects.create(
          board=group.board,
          title=form.cleaned_data['added_category'],
        )
      for category in form.cleaned_data['deleted_categories']:
        # 카테고리를 지울 시에 카테고리와 연결된 글들의 카테고리를 삭제해 주어야 한다.
        for bulletin in category.related_bulletin.all():
          bulletin.category = None
          bulletin.save()
        category.delete()
      return HttpResponseRedirect('/group/%d/manage/' % group.id)
  else:
    form = ManageGroupForm(group=group, data={
      'title':group.title,
      'desc':group.desc,
      'hidden':group.hidden,
    })

  tpl = loader.get_template('group/manage.html')    # manage.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니이다.
    "current_group":group,
    "is_member":group.members.filter(id=request.user.id).exists(),
    'is_semi_member':group.semi_members.filter(id=request.user.id).exists(),
    "form":form,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def invite_page(request, gid):
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if group.hidden and not group.members.filter(id=request.user.id).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임에 접근할 권한이'})
  if group.owner != request.user:
    return render_to_response('noExist.html',{'user':request.user, 'target':'관리자가 아닙니다. 권한이'})

  if request.method == "POST":
    form = InviteGroupForm(data=request.POST, group=group)
    if form.is_valid():
      sid = form.cleaned_data['sid']
      userProfile = UserProfile.objects.get(sid=sid)
      group.members.add(userProfile.user)
      Feed.objects.create(
        url="/group/%s/"%group.id,
        from_user=request.user,
        to_user=userProfile.user,
        additional=group.id,
        type=u'GI',
      )
      return HttpResponseRedirect("/group/%s/invite/"%group.id)
  else:
    form = InviteGroupForm(group=group)
  knowns = request.user.get_profile().knowns.all()
  for known in knowns:
    if group.semi_members.filter(id=known.id).exists():
      known.is_semi_member = True
    elif group.members.filter(id=known.id).exists():
      known.is_member = True

  tpl = loader.get_template('group/invite.html')    # invite.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    "current_group":group,
    "is_member":group.members.filter(id=request.user.id).exists(),
    'is_semi_member':group.semi_members.filter(id=request.user.id).exists(),
    'knowns':knowns,
    'form':form,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def invite_ajax(request, gid, sidHash):
  if checkCSRF_with_tval(request):
    return dealCSRF(request)
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if group.hidden and not group.members.filter(id=request.user.id).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임에 접근할 권한이'})
  if group.owner != request.user:
    return render_to_response('noExist.html',{'user':request.user, 'target':'관리자가 아닙니다. 권한이'})
  try:
    target = UserProfile.objects.get(sidHash=sidHash)
    target = target.user
  except ObjectDoesNotExist:
    return HttpResponse("해당 유저가 없습니다.")
  if group.members.filter(id=target.id).exists():
    return HttpResponse("이미 가입 되었습니다.")
  if group.semi_members.filter(id=target.id).exists():
    return HttpResponse("가입 승인중입니다.")
  group.members.add(target)
  return HttpResponse("초대완료")

@login_required
def members_page(request, gid):
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if group.hidden and not group.members.filter(id=request.user.id).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임에 접근할 권한이'})

  tpl = loader.get_template('group/members.html')    # invite.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    "current_group":group,
    "is_member":group.members.filter(id=request.user.id).exists(),
    'is_semi_member':group.semi_members.filter(id=request.user.id).exists(),
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def kick_page(request, gid, uid):
  group = get_group(gid)
  if group is None:  # 그룹이 없으면
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if group.hidden and not group.members.filter(id=request.user.id).exists(): # 히든그룹인데 멤버가 아니면
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임에 접근할 권한이'})
  if not group.owner == request.user:
    return render_to_response('noExist.html',{'user':request.user, 'target':'권한이'})
  user = User.objects.get(id=uid)
  if user == request.user:
    return render_to_response('noExist.html',{'user':request.user, 'target':'자기 자신은 강퇴할 수'})
  group.members.remove(user)
  return HttpResponseRedirect('/group/%d/members/'%int(gid))

@login_required
def remove_page(request, gid):
  group = get_group(gid)
  if group is None:  # 그룹이 없으면
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if not group.owner == request.user:
    return render_to_response('noExist.html',{'user':request.user, 'target':'권한이'})
  # 게시판을 삭제해 준다.
  group.board.delete()
  group.delete()
  return HttpResponseRedirect('/group/')

@login_required
def board_page(request, gid):
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})
  if group.hidden and not group.members.filter(id=request.user.id).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임에 접근할 권한이'})

  return HttpResponseRedirect('/board/%s/'%group.board.title)

@login_required
def chat_page(request, gid):
  group = get_group(gid)
  if group is None:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임이'})

  # 그룹 멤버가 아니면 채팅방을 못들어감!
  if not group.members.filter(id=request.user.id).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 소모임의 멤버가 아닙니다. 권한이'})

  tpl = loader.get_template('group/chat.html')    # chat.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    "current_group":group,
    "is_member":group.members.filter(id=request.user.id).exists(),
    'is_semi_member':group.semi_members.filter(id=request.user.id).exists(),
    "chat_hash":md5(b64encode(sha224(group.name).hexdigest())).hexdigest(),
  })
  return HttpResponse(tpl.render(ctx))

def get_group(gid):
  try:
    return Group.objects.get(id=int(gid))
  except ObjectDoesNotExist:
    return None

