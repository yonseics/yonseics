# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext, ugettext_lazy as _
from combaragi import settings
from combaragi.community.models import UserProfile, Memo, PointLog, Emblem, Feed, BlackList

admin.site.register(UserProfile)
admin.site.register(Memo)
admin.site.register(PointLog)
admin.site.register(Emblem)
admin.site.register(Feed)
admin.site.register(BlackList)

class MyUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        field_list = list()
        if request.user.is_superuser:
            field_list.append((None, {'fields': ('username', 'password')}))
        else:
            field_list.append((None, {'fields': ('password',)}))

        field_list.append((_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}))

        if request.user.is_superuser:
            perm_fields = ('is_active', 'is_staff', 'is_superuser',
                           'groups', 'user_permissions')
        else:
            # modify these to suit the fields you want your
            # staff user to be able to edit
            perm_fields = ('is_active', 'is_staff')

        field_list.append((_('Permissions'), {'fields': perm_fields}))

        if request.user.is_superuser:
            field_list.append((_('Important dates'), {'fields': ('last_login', 'date_joined')}))

        return field_list

    def user_change_password(self, request, id):
        ret = super(MyUserAdmin, self).user_change_password(request, id)
        if self.isPasswordChanged(ret):
            # Mail to user and admin that the password is changed.
            user = get_object_or_404(User, pk=id)
            user_name = user.get_profile().get_pure_full_name()
            my_name = request.user.get_profile().get_pure_full_name()
            targetList = []
            subject = u'[컴바라기] %s님의 비밀번호가 변경되었습니다.' % user_name
            content = u'%s님의 %s님에 의해 비밀번호가 변경되었습니다.\n<br/><br/>혹시 해당 요청을 하지 않았을 경우 학생회 측에 문의해 주세요.' % (user_name, my_name)
            for admin in settings.ADMINS:
                targetList.append(admin[1])
            targetList.append(user.email)
            try:
                email = EmailMessage(subject, content, from_email='noreply@yonseics.net', to=targetList)
                email.content_subtype = "html"
                email.send()
            except:
                pass
        return ret

    def isPasswordChanged(self, redirect):
        return redirect.status_code == 302 and 'location' in redirect and redirect['location'] == '..'

def user_unicode(self):
    try:
        return self.get_profile().get_pure_full_name()
    except:
        pass
    return self.username

User.__unicode__ = user_unicode

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)