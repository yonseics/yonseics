# -*- coding: utf-8 -*-
# Author: UNKI

from mail.forms import MailSendForm

from community.models import UserProfile
from community.views import error
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def main_page(request):
  if request.method == 'POST':
    form = MailSendForm(request.POST)
    if form.is_valid():
      subject = form.cleaned_data['subject']
      target = form.cleaned_data['target']
      content = form.cleaned_data['content']
      try:
        # 여기서 mail을 보냅니다.
        if target == '0':    # 내 학번에게
          sid = request.user.get_profile().sid
          if len(sid) == 7:  # 구 학번 시스템
            targets = UserProfile.objects.filter(sid__startswith=sid[0:2])
          else:         # 학번이 10자리인 신 학번 시스템
            targets = UserProfile.objects.filter(sid__startswith=sid[0:4])
        elif target == '1':    # 모두에게
          targets = UserProfile.objects.all()
        elif target == '2':    # 자신에게
          targets = [request.user.get_profile()]
        else:
          # 수상한 짓을 하려고 했습니다.
          return HttpResponse(u'그런 대상은 없습니다.')
        if target in ['0', '1']:
          targets = targets.filter(sendmail=True)
        targetList = []
        for t in targets:
          #if t.user.id is not request.user.id:    # 자기 자신을 제외하는 코드
          targetList.append(t.user.email)
        email = EmailMessage(subject, content, from_email='noreply@yonseics.net', to=targetList)  # 이메일 메시지를 보내봅니다.
        email.content_subtype = "html"  # 메인 contents를 text/html로 합니다.
        email.send()
      except BadHeaderError:        # 헤더가 이상한 경우
        return HttpResponse('Invalid header found.')
      except:
        return error(request, '메일을 보내는 도중 알 수 없는 에러가 발생하였습니다.')
      return HttpResponseRedirect('/mail/thanks/')
  else:
    form = MailSendForm()
  return render_to_response('mail/write.html',
                            context_instance=RequestContext(request, {
                              'form': form,
                            }))
