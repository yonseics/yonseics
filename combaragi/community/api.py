# -*- coding: utf-8 -*-
# Author: KIMSHIN
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from tastypie.resources import ModelResource
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.conf.urls.defaults import url
from tastypie.utils import trailing_slash
from tastypie.authorization import Authorization

# EXAMPLE
# 사용자 정보: curl http://yonseics.net/api/user/4/?format=json
# 로그인: curl -H "Content-Type: application/json" -d '{"username":"asdf","password":"asdfasdf"}' http://yonseics.net/api/user/login/;
# 로그아웃: curl http://yonseics.net/api/user/logout/

class CanOnlyReadOwnAuthorization(Authorization):
    """본인의 정보만 읽을 수 있습니다."""
    def read_detail(self, object_list, bundle):
        # TO DO: 401/403 메세지는 어떻게 할까요?
        return bundle.obj == bundle.request.user

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        allowed_methods = ['get', 'post']
        resource_name = 'user'
        excludes = ['password'] # 필요없는 정보는 여기에 추가합니다.
        authorization = CanOnlyReadOwnAuthorization()

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                    }, HttpForbidden )
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
                }, HttpUnauthorized )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized)
