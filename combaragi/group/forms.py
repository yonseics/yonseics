# -*- coding: utf-8 -*-
# Author: UNKI

import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from community.models import UserProfile
import group
from models import Group
from ccboard.models import Board, Category
from group.fields import UserModelChoiceField, UserModelMultipleChoiceField

class CreateGroupForm(forms.Form):
  title = forms.CharField(label='소모임 이름', max_length=20, widget=forms.TextInput(attrs={'class':'i_text'}))
  name = forms.CharField(label='소모임 영문이름', max_length=10, widget=forms.TextInput(attrs={'class':'i_text'}), help_text='알파벳, 숫자, 밑줄만 가능합니다.')
  desc = forms.CharField(label='소모임 설명', required=True, widget=forms.Textarea(attrs={'class':'textareaContent', 'rows':'20'}))
  hidden = forms.BooleanField(label='비밀 소모임 여부', required=False,
                              widget=forms.CheckboxInput(attrs={'no_overlabel':True}))

  def clean_name(self):
    name = self.cleaned_data['name']
    # \w는 문자나 숫자 혹은 밑줄 한글자를 뜻합니다.
    # +는 한개이상 일치하는 것을 찾겠다는 뜻입니다.
    if not re.search(r'^\w+$', name):
      raise forms.ValidationError('사용자 이름은 알파벳, 숫자, 밑줄(_)만 가능합니다.')
    try:
      Group.objects.get(name=name)
    except ObjectDoesNotExist:
      try:
        Board.objects.get(name=name)
      except ObjectDoesNotExist:
        return name
      raise forms.ValidationError('이미 사용중인 이름입니다')
    raise forms.ValidationError('이미 사용중인 이름입니다')

class ManageGroupForm(forms.Form):
  def __init__(self, group, *args, **kwargs):
    super(ManageGroupForm, self).__init__(*args, **kwargs)
    self.fields['owner'].queryset = group.members.exclude()
    self.fields['semi_members'].queryset = group.semi_members.all()
    self.fields['deleted_categories'].queryset = group.board.categories.all()
  title = forms.CharField(label='소모임 이름', max_length=20, widget=forms.TextInput(attrs={'class':'i_text'}))
  desc = forms.CharField(label='소모임 설명', required=True, widget=forms.Textarea(attrs={'class':'textareaContent', 'rows':'20'}))
  hidden = forms.BooleanField(label='비밀 소모임 여부', required=False,
                              widget=forms.CheckboxInput(attrs={'no_overlabel':True}))
  owner = UserModelChoiceField(
    label='소모임장 권한을 넘깁니다.',queryset=User.objects.none(),
    required=False, empty_label='----------',
    widget=forms.Select(attrs={'no_overlabel':True}))
  semi_members = UserModelMultipleChoiceField(
    label='회원 가입을 승인합니다.',queryset=User.objects.none(),
    required=False,
    widget=forms.SelectMultiple(attrs={'no_overlabel':True}))
  added_category = forms.CharField(required=False, label='소모임 게시판 카테고리추가', max_length=20, widget=forms.TextInput(attrs={'class':'i_text'}))
  deleted_categories = forms.ModelMultipleChoiceField(
    label='소모임 게시판 카테고리를 삭제합니다.',queryset=Category.objects.none(),
    required=False,
    widget=forms.SelectMultiple(attrs={'no_overlabel':True}))

  def clean_added_category(self):
    category_title = self.cleaned_data['added_category']
    if Category.objects.filter(title=category_title).exists():
      raise forms.ValidationError('이미 사용중인 이름입니다')
    return category_title

class InviteGroupForm(forms.Form):
  sid = forms.CharField(label='학번', max_length=10, widget=forms.TextInput(attrs={'class':'i_text'}), help_text='초청할 상대의 학번을 적어주세요.')
  def __init__(self, group, *args, **kwargs):
    super(InviteGroupForm, self).__init__(*args, **kwargs)
    self.group = group

  def clean_sid(self):
    sid = self.cleaned_data['sid']
    if UserProfile.objects.filter(sid=sid).exists():
      if self.group.members.filter(id=UserProfile.objects.get(sid=sid).user.id).exists():
        raise forms.ValidationError('이미 해당 유저는 초대된 상태입니다.')
      return sid
    raise forms.ValidationError('해당 학번을 가진 사람이 없습니다.')

