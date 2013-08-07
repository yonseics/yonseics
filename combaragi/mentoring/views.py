# -*- coding: utf-8 -*-
# Author: UNKI

from datetime import date
from django.conf import settings
from django.contrib.auth.decorators import login_required # 로그인 필수
from django.core.exceptions import ObjectDoesNotExist # 오브젝트가 없는 exception
from django.db.models import Count, Q # Aggregation을 위해
from django.http import HttpResponse, HttpResponseRedirect, \
  HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.views.decorators.cache import cache_page
from community.models import Feed
from mentoring.forms import SearchForm, QuestionWriteForm, QuestionReplyForm, RegisterMenteeForm, RegisterMentorForm
from mentoring.models import Relation
from mentoring.models import Mentor, Question
from tagging.models import Tag
#from community.models import UserProfile

"""
메인 페이지
  현재 자신의 정보: 멘토여부(멘토가 아니면 등록하기 가 있음), 현재 관계를 맺고있는 멘토 목록(나의 멘토), 나의 멘티, 최근 해결된 질문수, 총 미해결 질문수, 나의 옥수수, 내 질문(빨간색으로 괄호하고 수락되지 않은 답변수를 표시해 준다), 내 답변
  최근 올라온 미 해결 질문들
  최근 답변이 달린 질문들
  전체 질문
  내가 한 질문
  이달의 멘토 랭킹
  올해의 멘토 랭킹
  멘토들의 답변가능 분야(태그클라우드)
"""
def get_mentoring_info(user):
  try:
    mentor = Mentor.objects.get(user=user)
  except ObjectDoesNotExist:
    mentor = None

  return {
    'mentor' : mentor,
#    'recent_accepted_cnt' : Question.alls.filter(accepted=True).filter(updated__gte=datetime.now()-timedelta(days=1)).count(),    # 현재 날짜로 하루전날까지 글의 수
#    'recent_cnt' : Question.alls.filter(Q(updated__gte=datetime.now()-timedelta(days=1)), Q(mentor=None) | Q(mentor=user)).count(),                    # 현재 날짜로 하루전날까지 글의 수
#    'unsolved_cnt' : Question.alls.filter(Q(accepted=False), Q(mentor=None) | Q(mentor=user)).count(),
#    'my_unsolved_cnt' : Question.alls.filter(Q(mentee=user), Q(accepted=False), Q(mentor=None) | Q(mentor=user)).count(),
#    'my_recent_accepted_cnt' : Question.alls.filter(Q(replyingMentor=user), Q(accepted=True), Q(updated__gte=datetime.now()-timedelta(days=1)), Q(mentor=None) | Q(mentor=user)).count(),
    # 나의 멘토 수, 나의 멘티 수, 최근 질문 수/전체 질문 수, 최근 내 질문 수/전체 내 질문 수, 최근 내 답변 수/전체 내 답변 수
# 최근 나에게 올라온 질문
#    'recent_my_cnt' : Question.alls.filter(mentor=mentor).filter(updated__gte=datetime.now()-timedelta(days=1)).count(),    # 현재 날짜로 하루전날까지 글의 수
# 최근 올라온 질문
#    'recent_cnt' : Question.alls.filter(updated__gte=datetime.now()-timedelta(days=1)).count(),      # 현재 날짜로 하루전날까지 글의 수
# 내게 질문한 것중 해결되지 않은 질문수
#    'unsolved_cnt' : Question.alls.filter(Q(mentor=mentor), Q(reply=None)).count(),
#    'my_unsolved_cnt' : Question.alls.filter(mentee=user).filter(accepted=False).count(),
#    'my_recent_accepted_cnt' : Question.alls.filter(mentor=mentor).filter(accepted=True).filter(updated__gte=datetime.now()-timedelta(days=1)).count(),
    'mentor_cnt': Relation.objects.filter(Q(accepted=True), Q(mentee=user)).count(),      # 내 멘토의 숫자
    'wait_mentor_cnt': Relation.objects.filter(Q(accepted=False), Q(mentee=user)).count(),    # 아직 요청을 수락받지 않은 멘토의 숫자
    'mentee_cnt': Relation.objects.filter(Q(accepted=True), Q(mentor=mentor)).count(),    # 내 멘티의 숫자
    'wait_mentee_cnt': Relation.objects.filter(Q(accepted=False), Q(mentor=mentor)).count(),    # 아직 요청을 수락받지 못한 멘티의 숫자
    'total_recent_cnt': Question.recents.count(),            # 최근 질문의 숫자
    'total_total_cnt': Question.alls.count(),              # 모든 질문의 숫자
    'my_question_recent_cnt': Question.recents.filter(mentee=user).count(),    # 내 최근 질문의 숫자
    'my_question_total_cnt': Question.alls.filter(mentee=user).count(),      # 내 모든 질문의 숫자
    'my_reply_recent_cnt': Question.recents.filter(mentor=mentor).count(),    # 내 최근 답변의 숫자
    'my_reply_total_cnt': Question.alls.filter(mentor=mentor).count(),      # 내 모든 답변의 숫자
  }

# 자동완성을 위한...
def autocomplete(request, type):
  if type != 'tags' and not request.GET.get('q'):
    return HttpResponse(mimetype='text/plain')    # q가 없으면

  q = request.GET.get('q')
  prefix = q[:q.rfind(',')+1]
  q = q[q.rfind(',')+1:]
  def iter_results(results):
    if results:
      for r in results:
        if type == 'my_mentors':
          yield '%s\n' % r
        elif type == 'my_mentees':
          yield '%s\n' % r.mentee_name
        elif type == 'mentors':
          yield '%s\n' % r
        elif type == 'tags':
          yield '%s%s\n' % (prefix, r)
        elif type == 'questions':
          yield '%s\n' % r

  limit = request.GET.get('limit', 15)
  try:
    limit = int(limit)
  except ValueError:
    return HttpResponseBadRequest()

  if type == 'my_mentors':
    acData = map(lambda r: r.mentor.name, Relation.objects.filter(Q(mentee=request.user), Q(mentor__name__contains=q))[:limit])
    acData = acData + map(lambda r: r.name, Tag.objects.filter(name__contains=q)[:(limit - len(acData))])
  elif type == 'my_mentees':
    mentor = Mentor.objects.get(user=request.user)
    acData = Relation.objects.filter(Q(mentor=mentor), Q(mentee_name__contains=q))[:limit]
  elif type == 'mentors':
    acData = map(lambda r: r.name, Mentor.objects.filter(name__contains=q)[:limit])
    acData = acData + map(lambda r: r.name, Tag.objects.filter(name__contains=q)[:(limit - len(acData))])
  elif type == 'tags':
    acData = map(lambda t: t.name, Tag.objects.filter(name__contains=q))
    acData = list(set(acData)-set(prefix.split(',')))[:limit]
  elif type == 'questions':
    acData = map(lambda r: r.title, Question.objects.filter(Q(mentee=request.user), Q(title__contains=q))[:limit])
    acData = acData + list(set(map(lambda r: r.mentor.name, Question.objects.filter(Q(mentee=request.user), Q(mentor__name__contains=q))[:(limit - len(acData))])))
    acData = acData + list(set(map(lambda r: r.mentee.first_name, Question.objects.filter(Q(mentee=request.user), Q(mentee__first_name__contains=q))[:(limit - len(acData))])))
  else:
    acData = None
  return HttpResponse(iter_results(acData), mimetype='text/plain')

#autocomplete = cache_page(autocomplete, 60 * 60)  # 캐쉬해 놓습니당.


@login_required
def main_page(request):
#  user = request.user
#  recent_unsolved_5_question = Question.alls.filter(Q(replyingMentor=None), Q(mentor=None) | Q(mentor=user))[:5]
#  recent_solved_5_question = Question.alls.filter(Q(accepted=True), Q(mentor=None) | Q(mentor=user))[:5]
#  my_question = Question.alls.filter(Q(mentee=request.user), Q(mentor=None) | Q(mentor=user))[:5]
#  total_question = Question.alls.filter(Q(mentor=None) | Q(mentor=user))[:5]
#total_question = Question.alls.all()[:5]
  limit = 5
  try:
    mentor = Mentor.objects.get(user=request.user)
  except ObjectDoesNotExist:
    mentor = None

  if mentor:
    recent_unsolved_5_question = Question.unsolveds.filter(Q(mentor__user=request.user) | Q(mentee=request.user))[:limit]
    recent_solved_5_question = Question.solveds.filter(Q(mentor__user=request.user) | Q(mentee=request.user))[:limit]
  else:
    recent_unsolved_5_question = None
    recent_solved_5_question = None
  my_question = Question.alls.filter(mentee=request.user)[:limit]

  if mentor:
    question_list_list = {'해결되지 않은 질문': recent_unsolved_5_question,
                '해결된 질문': recent_solved_5_question,
#'모든 질문': total_question,
                '내 질문': my_question,
    }
    question_list_list['해결되지 않은 질문'].list_type='unsolved'
    question_list_list['해결된 질문'].list_type='solved'
  else:
    question_list_list = {'내 질문': my_question,}
  question_list_list['내 질문'].list_type='my'

  # 이달의 멘토랭킹과 올해의 멘토랭킹
#mom = Question.alls.filter(updated__gte=date.today().replace(day=1)).exclude(reply=None).annotate(num_mentors=Count('mentor'))
#moy = Question.alls.filter(updated__gte=date.today().replace(month=1, day=1)).exclude(reply=None).annotate(num_mentors=Count('mentor'))
  mom = Question.alls.filter(updated__gte=date.today().replace(day=1)).exclude(reply=None).values('mentor', 'mentor__name').annotate(Count('mentor')).order_by()
  moy = Question.alls.filter(updated__gte=date.today().replace(month=1, day=1)).exclude(reply=None).values('mentor', 'mentor__name').annotate(Count('mentor')).order_by()

  MAX_QUESTION_LENGTH = getattr(settings, 'MAX_QUESTION_LENGTH',20)
  for name, question_list in question_list_list.items(): #@UnusedVariable
    for question in question_list:
      if len(question.title) > MAX_QUESTION_LENGTH:
        question.title = question.title[:MAX_QUESTION_LENGTH]+'...'

  tpl = loader.get_template('mentoring/index.html')
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'question_list_list':question_list_list,
    'mom':mom,
    'moy':moy,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def list_page(request, list_type, page=1):
  key = request.GET.get('key', None)
  page = int(page)
  form = SearchForm(type='questions', data=request.GET)
  questionPerPage = getattr(settings, 'QUESTION_PER_PAGE', 15)         # 한 페이지에 표시하는 게시물 수 15개
  # 일단 멘토라면 멘토에게 온 질문과 멘티에게 간 질문 둘다...
  if list_type == 'solved' or list_type == 'unsolved':
    try:
      mentor = Mentor.objects.get(user=request.user)
    except ObjectDoesNotExist:
      return render_to_response('noExist.html',{'user':request.user, 'target':'멘토가 아닙니다. 열람할 권한이'})

  list = Question.objects
  if list_type == 'solved':
    list = list.filter(mentor=mentor).exclude(reply=None)
    list_type_name = '해결된 질문 '
  elif list_type == 'unsolved':
    list = list.filter(mentor=mentor).filter(reply=None)
    list_type_name = '해결되지 않은 질문 '
  elif list_type == 'my':
    list = list.filter(mentee=request.user)
    list_type_name = '내 질문 '
  else:
    list = list.all()
    list_type_name = '전체 '

  if key:
    list = list.filter(Q(title__contains=key) | Q(mentor__user__first_name__contains=key) | Q(mentee__first_name__contains=key))
  # 여기서 일단 리스트가 고정됨
  total_question = list.count()
  list = list[questionPerPage*(page-1):questionPerPage*page]

  if (page is not 1) and len(list) is 0:
    return HttpResponseRedirect('/mentoring/list/%s/' % list_type)    # 기본 페이지에 가자

  total_page = total_question / questionPerPage;    # 총 페이지
  if total_question % questionPerPage:  # 남는게 있으면
    total_page = total_page + 1     # 갯수 하나 늘려줌
  no_seq = total_question - (page-1) * questionPerPage     # 번호 시퀀스!
  for question in list:    # 게시물에 번호를 달아준다.
    question.no = no_seq
    no_seq = no_seq - 1

  page_before = page-5         # 이전 다섯 페이지
  page_after = page+5         # 다음 다섯 페이지
  sPage = max(1, page-4)          # 페이지 시작
  ePage = min(page+4, total_page) + 1   # 페이지 끝
  page_list = range(sPage, ePage)      # 페이지 리스트

  tpl = loader.get_template('mentoring/list.html')    # list.html이라는 페이지를 template로 하여 출력합니다.
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'form':form,        # 검색폼. 테스트용.
    'list_type':list_type,    # 리스트 종류
    'list_type_name':list_type_name,
    'page':page,        # 현재 페이지
    'total_page':total_page,  # 총 페이지
    'page_before':page_before,  # 이전 5장
    'page_after':page_after,  # 다음 5장
    'page_list':page_list,    # 페이지 리스트
    'question_list':list,    # 게시물 리스트
    })
  return HttpResponse(tpl.render(ctx))



@login_required
def question_write_page(request, qid=-1):
  target_mentor_id = int(request.GET.get('mentor_id', 0))
  parent = None
  if qid != -1:
    try:
      parent = Question.alls.get(id=qid)
    except ObjectDoesNotExist:
      parent = None
  # 만약 멘토가 없다면 질문 불가
  if not Relation.objects.filter(Q(mentee=request.user)&Q(accepted=True)).exists():
    return render_to_response('noExist.html',{'user':request.user, 'target':'자신의 멘토가 없어서 질문을 작성할 수'})
  # 여기서 만약 parent가 있다면 멘토 선택 가능
  mentorRelation = None
  if parent:
    try:
      mentorRelation = Relation.objects.filter(mentee=parent.mentee).get(mentor=parent.mentor)
    except ObjectDoesNotExist:
      return render_to_response('noExist.html',{'user':request.user, 'target':'[심각한 오류] 해당 멘토가'})
    if mentorRelation.mentee != request.user:
      return render_to_response('noExist.html',{'user':request.user, 'target':'해당 질문에 대해 추가질문을 할 권한이'})
  elif target_mentor_id:
    try:
      mentorRelation = Relation.objects.filter(mentee=request.user).get(mentor__id=target_mentor_id)
    except ObjectDoesNotExist:
      return render_to_response('noExist.html',{'user':request.user, 'target':'[심각한 오류] 해당 멘토가'})
    if mentorRelation.mentee != request.user:
      return render_to_response('noExist.html',{'user':request.user, 'target':'해당 질문에 대해 추가질문을 할 권한이'})

  if request.method == 'POST':
    form = QuestionWriteForm(request=request, data=request.POST)
    if form.is_valid():
      question, created = Question.alls.get_or_create(
        mentee=request.user,
        title=form.cleaned_data['title'],
        content=form.cleaned_data['content'],
        mentor=form.cleaned_data['mentor'].mentor,
        parent=parent
      )
      if created:
        # Feed를 달아준다.
        if len(question.title) > 20:
          additionalTitle = '%s...' % question.title[:17]
        else:
          additionalTitle = question.title[:20]
        Feed.objects.create(
          url="/mentoring/question/read/%s"%question.id,
          from_user=request.user,
          to_user=question.mentor.user,
          additional=additionalTitle,
          type=u'MQ',
        )
      return HttpResponseRedirect('/mentoring/')    # 멘토링 메인으로 가자
  else:
    if mentorRelation:
      form = QuestionWriteForm(request, {'mentor':mentorRelation})
    else:
      form = QuestionWriteForm(request)

  tpl = loader.get_template('mentoring/question/write.html')
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'form': form,
    'parent': parent,
    'ment_type': u'질문하기',
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def question_reply_page(request, qid):
  qid = int(qid)
  try:
    question = Question.alls.get(id=qid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 질문글이'})

  try:
    mentor = Mentor.objects.get(user=request.user)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'멘토가 아닙니다. 답변을 달 권한이'})

  if mentor != question.mentor:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 글에 맞는 멘토가 아닙니다. 답변을 달 권한이'})

  if request.method == 'POST':
    form = QuestionReplyForm(request.POST)
    if form.is_valid():
      if not question.reply:    # 답변이 없을 때만
        mentor.kernels += 1
        mentor.save()
      question.reply = form.cleaned_data['reply']
      question.read = False
      question.save()
      # Feed를 달아준다.
      if len(question.title) > 20:
        additionalReply = '%s...' % question.reply[:17]
      else:
        additionalReply = question.reply[:20]
      Feed.objects.create(
        url="/mentoring/question/read/%s"%question.id,
        from_user=request.user,
        to_user=question.mentee,
        additional=additionalReply,
        type=u'MR',
      )
      return HttpResponseRedirect('/mentoring/question/read/%d/' % qid)    # 멘토링 메인으로 가자
  else:
    if question.reply:
      form = QuestionReplyForm({'reply':question.reply})
    else:
      form = QuestionReplyForm()
  tpl = loader.get_template('mentoring/question/reply.html')
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'form': form,
    'question': question,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def question_read_page(request, qid):
  # 자기 글이나 멘토의 글만 읽을 수 있다.
  list_type = request.GET.get('listtype', None)
  page = request.GET.get('page', None)
  try:
    question = Question.alls.get(id=qid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 질문글이'})

  previous_question = question.parent
  next_question = Question.alls.filter(parent=question)

  # 읽어야 하는 사람이 읽었으면 read로 표시를 하자
  if question.mentor.user == request.user and not question.reply and not question.read or \
    question.mentee == request.user and question.reply and not question.read:
    question.read = True
    question.save()

  try:
    mentor = Mentor.objects.get(user=request.user)
  except ObjectDoesNotExist:
    mentor = None
  if mentor != question.mentor and request.user != question.mentee:
    return render_to_response('noExist.html',{'user':request.user, 'target':'글을 읽을 권한이'})

  tpl = loader.get_template('mentoring/question/read.html')
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'question': question,
    'mentor': mentor,
    'previous': previous_question,
    'next': next_question,
    'list_type':list_type,
    'page':page,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def question_modify_page(request, qid):
  qid = int(qid)
  try:
    question = Question.alls.get(id=qid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 질문글이'})

  if not hasAuthToModify(request, question):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 질문글을 수정할 권한이'})

  try:
    mentorRelation = Relation.objects.filter(mentee=question.mentee).get(mentor=question.mentor)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'[심각한 오류] 해당 멘토가'})

  if request.method == 'POST':
    form = QuestionWriteForm(request=request, data=request.POST)
    if form.is_valid():
      question.title=form.cleaned_data['title']
      question.content=form.cleaned_data['content']
      question.mentor=form.cleaned_data['mentor'].mentor
      question.save()
      return HttpResponseRedirect('/mentoring/question/read/%d/'%qid)    # 글 페이지로
  else:
    form = QuestionWriteForm(request=request, data={
      'title': question.title,
      'content': question.content,
      'mentor': mentorRelation,
    })
  tpl = loader.get_template('mentoring/question/write.html')
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'question': question,
    'form': form,
    'ment_type': u'수정하기',
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def question_delete_page(request, qid):
  qid = int(qid)
  try:
    question = Question.alls.get(id=qid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 질문글이'})

  if not hasAuthToModify(request, question):
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 질문글을 삭제할 권한이'})

  question.delete()    # 삭제 해준다

  return HttpResponseRedirect('/mentoring/')

@login_required
def mentors_info_page(request):
  key = request.GET.get('key')
  if key:
    mentorList = Mentor.objects.filter(Q(name__contains=key) | Q(tags__contains=key))
  else:
    mentorList = Mentor.objects.all()
  for mentor in mentorList:
    mentor.menteeCnt = Relation.objects.filter(Q(accepted=True), Q(mentor=mentor)).count()    # 멘토 숫자를 따로 넣어준다
    mentor.replyCnt = Question.alls.filter(mentor=mentor).count()    # 멘토 숫자를 따로 넣어준다
    mentor.tags = map(lambda str:str.strip(' '), mentor.tags.split(','))
    if mentor.user == request.user:    # 자기 자신이면
      mentor.related = '나'       # 이미 연관됨
    else:
      try:
        relation = Relation.objects.get(Q(mentee=request.user, mentor=mentor))    # 릴레이션을 가져올 수 있다면
        if relation.accepted:
          mentor.related = 'Yes'        # 이미 연관됨
        else:
          mentor.related = '대기'           # 이미 연관됨
      except ObjectDoesNotExist:      # 없으면
        mentor.related = False       # 연관 없음
  tpl = loader.get_template('mentoring/info/mentors.html')
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'mentorList': mentorList,
    'search_form': SearchForm(type='mentors', data=request.GET),
    'type':u'모든',
    'allMentor':True,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def my_mentors_info_page(request):
#  mentorList = Mentor.objects.filter(mentee=request.user)
  key = request.GET.get('key')
  if key:
    mentorRelationList = Relation.objects.filter(Q(mentee=request.user), (Q(mentor__name__contains=key) | Q(mentor__tags__contains=key)))
  else:
    mentorRelationList = Relation.objects.filter(Q(mentee=request.user))
  for relation in mentorRelationList:
    relation.mentor.relation = relation
  mentorList = map(lambda relation: relation.mentor, mentorRelationList)
  for mentor in mentorList:
    mentor.menteeCnt = Relation.objects.filter(Q(accepted=True), Q(mentor=mentor)).count()    # 멘토 숫자를 따로 넣어준다
    mentor.replyCnt = Question.alls.filter(mentor=mentor).count()    # 멘토 숫자를 따로 넣어준다
    mentor.tags = map(lambda str:str.strip(' '), mentor.tags.split(','))
  tpl = loader.get_template('mentoring/info/mentors.html')
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'mentorList': mentorList,
    'type':u'나의',
    'search_form': SearchForm(type='my_mentors', data=request.GET),
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def my_mentees_info_page(request):
  try:
    mentor = Mentor.objects.get(user=request.user)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'당신은 멘토가 아닙니다. 멘토 정보가'})

  key = request.GET.get('key')
  if key:
    menteeRelationList = Relation.objects.filter(Q(mentor=mentor), (Q(mentee_name__contains=key) | Q(mentor__tags__contains=key)))
  else:
    menteeRelationList = Relation.objects.filter(Q(mentor=mentor))

  for relation in menteeRelationList:
    relation.question_cnt = Question.alls.filter(mentee=request.user).count()

  tpl = loader.get_template('mentoring/info/mentees.html')
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'menteeRelationList': menteeRelationList,
    'search_form': SearchForm(type='my_mentees', data=request.GET),
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def register_mentor_page(request):
  tpl = loader.get_template('mentoring/registerMentor.html')
  if request.method == 'POST':
    form = RegisterMentorForm(request.POST)
    if form.is_valid():
      Mentor.objects.create(
        user=request.user,
        name=request.user.get_profile().get_pure_full_name(),
        tags=form.cleaned_data['tags'],
      )
      return HttpResponseRedirect('/mentoring/')    # 메인 페이지로
  else:
    form = RegisterMentorForm()
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'form': form,
  })
  return HttpResponse(tpl.render(ctx))

@login_required
def register_mentee_page(request, mid):
  try:
    mentor = Mentor.objects.get(id=mid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 멘토가'})

  tpl = loader.get_template('mentoring/registerMentee.html')
  if request.method == 'POST':
    form = RegisterMenteeForm(request.POST)
    if form.is_valid():
      relation, created = Relation.objects.get_or_create(
        mentor_id=mid,
        mentee=request.user,
        mentee_name=request.user.get_profile().get_pure_full_name(),
        request_msg=form.cleaned_data['msg'],
      )
      if created:
        # Feed를 달아준다.
        msg = form.cleaned_data['msg']
        if len(msg) > 20:
          additionalMsg= '%s...' % msg[:17]
        else:
          additionalMsg = msg[:20]
        Feed.objects.create(
          url="/mentoring/myinfo/mentees/",
          from_user=request.user,
          to_user=Mentor.objects.get(id=mid).user,
          additional=additionalMsg,
          type=u'MI',
        )
      return HttpResponseRedirect('/mentoring/')    # 메인 페이지로
  else:
    form = RegisterMenteeForm()
  ctx = RequestContext(request, {            # parameter를 dictionary형식으로 넣을 수 있습니다.
    'info': get_mentoring_info(request.user),    # 모든 멘토링 페이지에는 이 줄을 넣어야 합니다.
    'form': form,
    'mentor': mentor,
  })
  return HttpResponse(tpl.render(ctx))

# 멘토를 수락함
@login_required
def accept_mentee_page(request, rid):
  try:
    relation = Relation.objects.get(id=rid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 릴레이션이'})

  try:
    mentor = Mentor.objects.get(user=request.user)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'당신은 멘토가 아닙니다. 멘토 정보가'})

  if mentor == relation.mentor and not relation.accepted:    # 자기 자신의 릴레이션일 경우에만
    relation.accepted = True
    relation.save()
    # Feed를 달아준다.
    Feed.objects.create(
      url="/mentoring/myinfo/mentors/",
      from_user=relation.mentor.user,
      to_user=relation.mentee,
      additional=None,
      type=u'MA',
    )
  return HttpResponseRedirect('/mentoring/')    # 메인 페이지로

# 멘토를 거절함
@login_required
def deny_mentee_page(request, rid):
  try:
    relation = Relation.objects.get(id=rid)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'해당 릴레이션이'})

  try:
    mentor = Mentor.objects.get(user=request.user)
  except ObjectDoesNotExist:
    return render_to_response('noExist.html',{'user':request.user, 'target':'당신은 멘토가 아닙니다. 멘토 정보가'})

  if mentor == relation.mentor:    # 자기 자신의 릴레이션일 경우에만
    relation.delete()
  return HttpResponseRedirect('/mentoring/')    # 메인 페이지로

def hasAuthToModify(request, question):
  if question.reply:
    return False
  if question.mentee == request.user:
    return True
  return False
