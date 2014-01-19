# -*- coding: utf-8 -*-
# Author: UNKI

import re
from random import randint
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from community.models import UserProfile
from community.rsa import decrypt
from unicodedata import normalize

# Django 기본 패키지에서 가져옴
from combaragi.community.models import RegisterQuiz

class AuthenticationForm(forms.Form):
  """
  Base class for authenticating users. Extend this to get a form that accepts
  username/password logins.
  """
  username = forms.CharField(label='ID', max_length=30, widget=forms.TextInput(attrs={'class':'i_text medium', 'size':30}))
  password = forms.CharField(label='암호', max_length=100, widget=forms.PasswordInput(attrs={'class':'i_text medium', 'size':30}))

  def clean(self):
    if ('username' not in self.cleaned_data or
        'password' not in self.cleaned_data):
      raise forms.ValidationError("아이디나 패스워드를 꼭 입력해 주세요.")
    username = self.cleaned_data['username']
    password = self.cleaned_data['password']

    if username and password:
      # 여기서 세션키를 사용하여 암호를 해독합니다.
      self.user_cache = authenticate(username=username, password=password)
      if self.user_cache is None:
        raise forms.ValidationError("ID가 틀렸거나 패스워드가 틀렸습니다. 패스워드는 대소문자를 구분합니다.")
      elif not self.user_cache.is_active:
        raise forms.ValidationError("이 계정은 사용중지 되었습니다.")

    return self.cleaned_data

  def get_user_id(self):
    if self.user_cache:
      return self.user_cache.id
    return None

  def get_user(self):
    return self.user_cache

class RegistrationForm(forms.Form):

  def __init__(self, qid=None, *args, **kwargs):
    if not RegisterQuiz.actives.exists():
      RegisterQuiz.objects.create(question=u'연세대학교 학생이십니까? (예/아니오)', answer=u'예')
    if qid:
      quiz = RegisterQuiz.actives.get(id=qid)
    else:
      quiz = RegisterQuiz.actives.all()[randint(0, RegisterQuiz.actives.count() - 1)]
    super(RegistrationForm, self).__init__(*args, **kwargs)
    self.fields['question_type'].initial = quiz.pk
    self.fields['question'].help_text = quiz.question

  username = forms.CharField(label='(*) 아이디', max_length=30, widget=forms.TextInput(attrs={'class':'i_text'}))    # 유저 이름
  password1 = forms.CharField(        # 패스워드.
      label='(*) 비밀번호',
      widget=forms.PasswordInput(attrs={'class':'i_text'})    # 패스워드 형식으로 한다.
      )
  password2 = forms.CharField(        # 역시 패스워드와 마찬가지로
      label='(*) 비밀번호(확인용)',
      widget=forms.PasswordInput(attrs={'class':'i_text'})
      )
  email = forms.EmailField(label='(*) 이메일')        # 이메일
  sid = forms.CharField(label='(*) 학번', max_length=10)
  realname = forms.CharField(label='(*) 실명', max_length=20, help_text='반드시 실명만 기재바랍니다.')
  gender = forms.ChoiceField(widget=forms.RadioSelect, label='', choices=UserProfile.GENDER_CHOICES)  # 성별. M이나 F만 가능합니다.
  status = forms.ChoiceField(widget=forms.RadioSelect, label='', choices=UserProfile.STATUS_CHOICES)  # 재학여부
  jobpos = forms.CharField(label='연구실/직장명', max_length=50, required=False, help_text='학부생은 연세대학교라고 적어주세요.')
  address = forms.CharField(label='주소', max_length=255, required=False)
  homepageURL = forms.URLField(label='홈페이지', required=False)      # 홈페이지 URL
  birthday = forms.DateField(label='생년월일', required=False, help_text='형식: 년 - 월 - 일 (예: 1986-02-19)')      # 생년월일
  phone = forms.CharField(label='연락처', max_length=15, required=False)  # 전화번호
  sendmail = forms.BooleanField(label='메일수신여부',
                                help_text='컴바라기에서 보내지는 메일을 수신합니다. 학과 공지등 중요한 메일이 날아갈 수 있으니 가급적이면 수신해 주세요.',
                                required=False,
                                initial=True,
                                widget=forms.CheckboxInput(attrs={'no_overlabel':True}))    # 메일수신 여부
  portrait = forms.ImageField(label=u'초상화', required=False, widget=forms.FileInput(attrs={'no_overlabel': True}))
  introduction = forms.CharField(label='자기소개', required=False, widget=forms.Textarea)
  question_type = forms.CharField(widget=forms.HiddenInput())
  question = forms.CharField(label='(*) 가입퀴즈', required=True)

  def clean_question(self):
    qid = int(self.cleaned_data['question_type'])
    q = RegisterQuiz.actives.get(id=qid)
    if q.answer != self.cleaned_data['question']:
      raise forms.ValidationError('문제의 정답이 아닙니다.')
    return self.cleaned_data['question']

  def clean_password2(self):              # clean_<필드이름>으로 입력값을 확인할 수 있다.
    if 'password1' in self.cleaned_data:      # 만약 password1이 올바른 값이면
      password1 = self.cleaned_data['password1']  # password1받고
      password2 = self.cleaned_data['password2']  # password2받아서
      if password1 == password2:          # 확인합니다.
        return password2
    raise forms.ValidationError('비밀번호가 일치하지 않습니다.')

  def clean_username(self):
    username = self.cleaned_data['username']
    # \w는 문자나 숫자 혹은 밑줄 한글자를 뜻합니다.
    # +는 한개이상 일치하는 것을 찾겠다는 뜻입니다.
    if not re.search(r'^\w+$', username):
      raise forms.ValidationError('사용자 이름은 알파벳, 숫자, 밑줄(_)만 가능합니다.')
    try:
      User.objects.get(username=username)
    except ObjectDoesNotExist:
      return username
    raise forms.ValidationError('이미 사용중인 사용자 이름입니다')

  def clean_sid(self):
    sid = self.cleaned_data['sid']
    # \d는 숫자 한글자<p>를 뜻합니다.
    # +는 한개이상 일치하는 것을 찾겠다는 뜻입니다.
    if not re.search(r'^\d{7}$|^\d{10}$', sid):
      raise forms.ValidationError('정상적인 학번이 아닙니다')
    try:
      UserProfile.objects.get(sid=sid)
    except ObjectDoesNotExist:
      return sid
    raise forms.ValidationError('이미 사용중인 학번입니다. 관리자에게 문의하세요.')

class ModificationForm(forms.Form):
  password1 = forms.CharField(        # 패스워드.
    label='(*) 비밀번호',
    widget=forms.PasswordInput(attrs={'class':'i_text'}),    # 패스워드 형식으로 한다.
    required=False,
    help_text='비밀번호 칸은 수정시에만 입력해 주시기 바랍니다.'
  )
  password2 = forms.CharField(        # 역시 패스워드와 마찬가지로
    label='(*) 비밀번호(확인용)',
    widget=forms.PasswordInput(attrs={'class':'i_text'}),
    required=False
  )
  email = forms.EmailField(label='(*) 이메일')        # 이메일
  status = forms.ChoiceField(widget=forms.RadioSelect, label='', choices=UserProfile.STATUS_CHOICES)  # 재학여부
  jobpos = forms.CharField(label='연구실/직장명', required=False, max_length=50, help_text='학부생은 연세대학교라고 적어주세요.')
  address = forms.CharField(label='주소', max_length=255, required=False)
  homepageURL = forms.URLField(label='홈페이지', required=False)      # 홈페이지 URL
  birthday = forms.DateField(label='생년월일', required=False, help_text='형식: 년 - 월 - 일 (예: 1986-02-19)')      # 생년월일 'readonly':'true'
  phone = forms.CharField(label='연락처', max_length=15, required=False)  # 전화번호
  sendmail = forms.BooleanField(label='메일수신여부', help_text='컴바라기에서 보내지는 메일을 수신합니다.', required=False, widget=forms.CheckboxInput(attrs={'no_overlabel':True}))    # 메일수신 여부
  portrait = forms.ImageField(label=u'초상화', required=False, widget=forms.FileInput(attrs={'no_overlabel': True}))
  introduction = forms.CharField(label='자기소개', required=False, widget=forms.Textarea)

  def clean_password2(self):              # clean_<필드이름>으로 입력값을 확인할 수 있다.
    if 'password1' in self.cleaned_data:      # 만약 password1이 올바른 값이면
      password1 = self.cleaned_data['password1']  # password1받고
      password2 = self.cleaned_data['password2']  # password2받아서
      if password1 == password2:          # 확인합니다.
        return password2
    raise forms.ValidationError('비밀번호가 일치하지 않습니다.')

class GuestbookForm(forms.Form):
  content = forms.CharField(required=True, widget=forms.Textarea(attrs={'class':'i_textarea', 'rows':'15'}))
