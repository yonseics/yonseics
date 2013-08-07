# -*- coding: utf-8 -*-
# Author: UNKI
from community.views import error
from photologue.models import Gallery

from tower.forms import *
from tower.models import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.generic.simple import direct_to_template

def MyTower(request, tower):
  return request.user == tower.owner

@login_required
def main(request):
  cleared_towers = [info.tower for info in ClimbInfo.objects.filter(Q(tower__opened=True) &
                                                                       Q(user=request.user) &
                                                                       Q(cleared=True))]
  uncleared_towers = list(set(Tower.objects.filter(opened=True)).difference(cleared_towers))
  return direct_to_template(request, 'tower/index.html', {
    'cleared_towers': cleared_towers,
    'uncleared_towers': uncleared_towers,
    'building_towers': Tower.objects.filter(owner=request.user).filter(opened=False),
    'climb_infos': ClimbInfo.objects.all()[:20],
  })

@login_required
def create_tower(request):
  if request.method == 'POST':
    form = CreateTowerForm(request.POST, request.FILES)
    if form.is_valid():
      tower = Tower.objects.create(
        slug=form.cleaned_data['slug'],
        name=form.cleaned_data['name'],
        owner=request.user,
        image=form.cleaned_data['image'],
        difficulty=form.cleaned_data['difficulty'],
      )
      for guard in form.cleaned_data['guards']:
        tower.guards.add(guard)
      return HttpResponseRedirect(reverse('tower-main'))
  else:
    form = CreateTowerForm()
  return direct_to_template(request, 'tower/create.html', {
    'form': form,
  })

@login_required
def modify_tower(request, tower_slug):
  tower = get_object_or_404(Tower, slug=tower_slug)
  if not MyTower(request, tower):
    return error(request, '내가 생성한 탑이 아닙니다.')
  if tower.opened:
    return error(request, '탑이 이미 개방되어 수정할 수 없습니다.')
  if request.method == 'POST':
    form = ModifyTowerForm(request.POST, request.FILES)
    if form.is_valid():
      tower.name=form.cleaned_data['name']
      tower.difficulty=form.cleaned_data['difficulty']
      tower.guards.clear()
      for guard in form.cleaned_data['guards']:
        tower.guards.add(guard)
      tower.save()
      return HttpResponseRedirect(reverse('tower-modify', args=[tower_slug]))
  else:
    form = ModifyTowerForm(initial={
      'name': tower.name,
      'difficulty': tower.difficulty,
      'guard': tower.guards.all(),
    })
  return direct_to_template(request, 'tower/modify.html', {
    'form': form,
    'tower': tower,
  })

@login_required
def info(request, tower_slug):
  tower = get_object_or_404(Tower, slug=tower_slug)
  if not tower.opened and not MyTower(request, tower):
    return error(request, '탑이 아직 개방되어 있지 않습니다.')
  climb_info, created = ClimbInfo.objects.get_or_create(tower=tower, user=request.user)
  return direct_to_template(request, 'tower/info.html', {
    'tower': tower,
    'climb_info': climb_info,
  })

@login_required
def open(request, tower_slug):
  tower = get_object_or_404(Tower, slug=tower_slug)
  if not MyTower(request, tower):
    return error(request, '내가 생성한 탑이 아닙니다.')
  if not tower.levels.exists():
    return error(request, '탑에 층이 하나도 없습니다. 일단 층을 추가해 주세요!')
  if tower.opened:
    return error(request, '이미 탑이 열려 있습니다.')
  if request.method == 'POST':
    tower.opened = True
    tower.save()
    return HttpResponseRedirect(reverse('tower-info', args=[tower_slug]))
  return direct_to_template(request, 'tower/open.html', {
    'tower': tower,
  })

@login_required
def level(request, tower_slug, lv):
  skip = request.GET.get('skip', False)
  tower = get_object_or_404(Tower, slug=tower_slug)
  level = get_object_or_404(Level, Q(tower=tower) & Q(level=lv))
  climb_info = get_object_or_404(ClimbInfo, Q(tower=tower) & Q(user=request.user))
  if not tower.opened:
    return error(request, "탑이 아직 오픈되어 있지 않습니다. 탑을 오픈해서 사람들이 문제를 풀 수 있도록 해주세요!")
  if int(climb_info.current_level) < int(lv):
    raise Http404("잘못된 접근입니다.")
  climb_level_info, created = ClimbLevelInfo.objects.get_or_create(level=level, user=request.user)
  # 만들어 졌으면 climb_info에서 해당 층에 하나의 예제를 부여한다.
  if created:
    try:
      climb_level_info.set_random_case()
    except:
      climb_level_info.delete()
      raise
    climb_level_info.save()
  else:
    if not climb_level_info.current_case:
      climb_level_info.set_random_case()
      climb_level_info.save()
  if request.method == 'POST':
    form = SubmitForm(climb_level_info.current_case.output, request.POST)
    if form.is_valid():
      max_level = tower.max_level()
      if climb_info.current_level >= max_level:
        climb_info.current_level = max_level
        climb_info.cleared = True
        climb_info.save()
        return HttpResponseRedirect(reverse('tower-info', args=[tower_slug]))
      else:
        climb_info.current_level += 1
        climb_info.save()
        return HttpResponseRedirect(reverse('tower-level', args=[tower_slug, climb_info.current_level]))
  else:
    form = SubmitForm(climb_level_info.current_case.output)
  # Serialize message
  json_serializer = serializers.get_serializer("json")()
  msgs = json_serializer.serialize(level.messages.all(), ensure_ascii=False, use_natural_keys=True)
  return direct_to_template(request, 'tower/level.html', {
    'tower': tower,
    'level': level,
    'climb_level_info': climb_level_info,
    'msgs': msgs,
    'form': form,
    'skip': skip,
  })

@login_required
def create_level(request, tower_slug):
  tower = get_object_or_404(Tower, slug=tower_slug)
  if not MyTower(request, tower):
    return error(request, '내가 생성한 탑이 아닙니다.')
  if request.method == 'POST':
    form = CreateLevelForm(request.POST)
    if form.is_valid():
      level = Level.objects.create(
        tower=tower,
        level=tower.max_level() + 1,
        question=form.cleaned_data['question'],
        hint=form.cleaned_data['hint'],
      )
      count = int(request.POST['in_out'])
      for i in range(count):
        input = request.POST['id_in_out_in_%d' % (i + 1)]
        output = request.POST['id_in_out_out_%d' % (i + 1)]
        Case.objects.create(
          level=level,
          input=input,
          output=output,
        )
      return HttpResponseRedirect(reverse('tower-info', args=[tower_slug]))
  else:
    form = CreateLevelForm()

  return direct_to_template(request, 'tower/create_level.html', {
    'tower': tower,
    'form': form,
  })

@login_required
def message_add(request, tower_slug, lv, order='direct'):
  tower = get_object_or_404(Tower, slug=tower_slug)
  if not MyTower(request, tower):
    return error(request, '내가 생성한 탑이 아닙니다.')
  level = get_object_or_404(Level, Q(tower=tower) & Q(level=lv))
  if order == 'direct':
    messages = level.messages.all()
  else:
    messages = level.messages.order_by('-order')
  if request.method == 'POST':
    form = AddMessageForm(data=request.POST)
    if form.is_valid():
      action_image = get_object_or_404(ActionImage, id=form.cleaned_data['action_image_idx'])
      message = form.cleaned_data['message']
      message = message.replace('\r\n', '<br />')
      message = message.replace('\n', '<br />')
      Message.objects.create(
        level=level,
        order=level.get_next_message_order() + 1,
        message=message,
        action_image=action_image,
      )
      if order == 'direct':
        return HttpResponseRedirect(reverse('tower-add-message', args=[tower_slug, lv]))
      else:
        return HttpResponseRedirect(reverse('tower-add-message-reverse', args=[tower_slug, lv, order]))
  else:
    form = AddMessageForm()
  return direct_to_template(request, 'tower/message/add.html', {
    'tower': tower,
    'level': level,
    'form': form,
    'level_messages': messages,
  })

@login_required
def guards(request):
  return direct_to_template(request, 'tower/guards.html', {
    'guards': Guard.objects.all(),
  })

@login_required
def info_guard(request, gid):
  guard = get_object_or_404(Guard, id=gid)
  return direct_to_template(request, 'tower/guard.html', {
    'guard': guard,
    })

@login_required
def create_guard(request):
  if request.method == 'POST':
    form = CreateGuardForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('tower-guards'))
  else:
    form = CreateGuardForm()
  return direct_to_template(request, 'tower/create_guard.html', {
    'form': form,
  })

@login_required
def create_action_image(request, gid):
  guard = get_object_or_404(Guard, id=gid)
  if request.method == 'POST':
    form = CreateActionImageForm(guard, data=request.POST, files=request.FILES)
    if form.is_valid():
      action_photo=form.cleaned_data['action_photo']
      action_image = ActionImage.objects.create(
        guard=guard,
        name=form.cleaned_data['name'],
      )
      photo = Photo.objects.create(
        title=u'%s의 액션 이미지: %s' % (request.user.first_name, form.cleaned_data['name']),
        title_slug='action_image_%d' % action_image.id,
        image=action_photo,
      )
      action_image.photo = photo
      action_image.save()
      return HttpResponseRedirect(reverse('tower-info-guard', args=[gid]))
  else:
    form = CreateActionImageForm(guard)
  return direct_to_template(request, 'tower/action_image/add.html', {
    'form': form,
    'guard': guard,
  })
