# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from django.views.generic.simple import direct_to_template
from combaragi import settings
from combaragi.bomb.forms import BombCreateForm
from combaragi.bomb.models import Bomb, BombAlarm
from combaragi.ccboard.templatetags.time_filters import humanizeTimeDiff


class BombListView(ListView):
    model = Bomb
    template_name = 'bomb/list.html'
    context_object_name = 'bomb_list'

    def get_queryset(self):
        return Bomb.objects.filter(Q(user=self.request.user) | Q(private=False))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BombListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # check outdated bomb alarms
        alert_list = BombAlarm.objects.filter(time__lt=datetime.now())
        for alert in alert_list:
            due = humanizeTimeDiff(alert.bomb.getDueDate())
            subject = u'[컴바라기] 폭탄이 터지기 까지 %s 남았습니다.' % due
            content = u'폭탄(%s)이 터지기까지 %s 남았습니다. 해당 폭탄이 필요하다면 빠르게 회수하세요!' % (alert.bomb.title, due)
            try:
                email = EmailMessage(subject, content, from_email='noreply@yonseics.net', to=alert.bomb.user.email)
                email.content_subtype = "html"
                email.send()
            except:
                pass
            alert.delete()
        # check outdated bombs
        deleted_list = Bomb.objects.filter(uploaded__lt=datetime.now() - timedelta(days=settings.BOMB_TIME_DAYS))
        for deleted in deleted_list:
            # mail to the user of bomb user.
            subject = u'[컴바라기] 당신의 폭탄이 터졌습니다.'
            content = u'폭탄(%s)이 터졌습니다.' % deleted.title
            try:
                email = EmailMessage(subject, content, from_email='noreply@yonseics.net', to=deleted.user.email)
                email.content_subtype = "html"
                email.send()
            except:
                pass
        deleted_list.delete()
        context = super(BombListView, self).get_context_data(**kwargs)
        context['bomb_time'] = settings.BOMB_TIME_DAYS
        context['total'] = Bomb.objects.count()
        context['used'] = Bomb.getMyUsed(self.request.user)
        context['given'] = settings.BOMB_SPACE_PERSONAL
        return context


@login_required
def create_bomb_view(request):
    if request.method == 'POST':
        form = BombCreateForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            bomb = form.save(False)
            bomb.user = request.user
            bomb.save()
            for alarm_before in settings.BOMB_ALARM_BEFORE:
                before = timedelta(days=alarm_before[0], hours=alarm_before[1], minutes=alarm_before[2])
                alarm_time = bomb.getDueDate() - before
                BombAlarm.objects.create(bomb=bomb, time=alarm_time)
            return HttpResponseRedirect(reverse('bomb-list'))
    else:
        form = BombCreateForm(user=request.user)
    return direct_to_template(request, "bomb/create.html", {
        'form': form,
    })


@login_required
def delete_bomb_view(request, bid):
    try:
        Bomb.objects.get(id=bid).delete()
    except ObjectDoesNotExist:
        pass
    return HttpResponseRedirect(reverse('bomb-list'))
