# -*- coding: utf-8 -*-
# Author: UNKI

import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from community.models import UserProfile
from tower import widgets
from tower.models import *

class CreateTowerForm(forms.ModelForm):
  class Meta:
    model = Tower
    exclude = ('owner', 'opened')


class CreateGuardForm(forms.ModelForm):
  class Meta:
    model = Guard
  def clean_name(self):
    name = self.cleaned_data['name']
    if Guard.objects.filter(name=self.cleaned_data['name']).exists():
      raise ValidationError('이미 같은 이름을 가진 지킴이가 있습니다.')
    return name


class ModifyTowerForm(forms.ModelForm):
  class Meta:
    model = Tower
    exclude = ('owner', 'opened', 'image', 'slug')


class CreateLevelForm(forms.ModelForm):
  in_out = forms.IntegerField(widget=widgets.MultipleInputOutput, label='입출력', help_text='앞의 것이 입력, 뒤의 것이 출력입니다.')
  class Meta:
    model = Level
    exclude = ('tower', 'level')
  def clean_in_out(self):
    super(CreateLevelForm, self).clean()
    if 'in_out' in self.cleaned_data:
      try:
        in_out_count = int(self.cleaned_data['in_out'])
      except:
        raise ValidationError(u'수상한 짓을 하려고 했습니다.')
      if in_out_count < 1:
        raise ValidationError(u'최소한 한개의 테스트케이스가 필요합니다.')
      for i in range(in_out_count):
        input = self.data['id_in_out_in_%d' % (i + 1)]
        output = self.data['id_in_out_out_%d' % (i + 1)]
        if not input or not output:
          raise ValidationError(u'비어있는 테스트 케이스가 있습니다.')
      return in_out_count
    raise ValidationError(u'수상한 짓을 하려고 했습니다.')


class ModifyLevelForm(forms.Form):
  pass


class ActionImageChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    return '<%s>' % obj.__unicode__()


class AddMessageForm(forms.ModelForm):
  action_image_idx = forms.IntegerField(widget=forms.HiddenInput())
  #action_image = ActionImageChoiceField(ActionImage, label='액션 이미지', widget=forms.RadioSelect)

  #def __init__(self, tower, *args, **kwargs):
  #  super(AddMessageForm, self).__init__(*args, **kwargs)
  #  self.fields["action_image"].queryset = ActionImage.objects.filter(guard__guarding_towers=tower)

  class Meta:
    model = Message
    exclude = ('level', 'order', 'action_image')
    widgets = {
      'message': forms.Textarea(attrs={'class': 'action_text' }),
    }

  def clean_action_image_id(self):
    if 'action_image_id' not in self.cleaned_data:
      raise ValidationError('액션 이미지를 선택하셔야 합니다.')
    return self.cleaned_data


class SubmitForm(forms.Form):
  answer = forms.CharField(label=u'정답', widget=forms.Textarea(attrs={'class':'answer', 'rows':'10'}))

  def __init__(self, output, *args, **kwargs):
    super(SubmitForm, self).__init__(*args, **kwargs)
    self.output = output

  def clean_answer(self):
    answer = self.cleaned_data['answer']
    if answer.strip() != self.output:
      raise forms.ValidationError(u'정답이 아닙니다.')
    return answer


class CreateActionImageForm(forms.ModelForm):
  action_photo = forms.ImageField(label='이미지 업로드')

  def __init__(self, guard, *args, **kwargs):
    super(CreateActionImageForm, self).__init__(*args, **kwargs)
    self.guard = guard
  class Meta:
    model = ActionImage
    exclude = ('guard', 'photo')
  def clean_name(self):
    name = self.cleaned_data['name']
    if ActionImage.objects.filter(guard=self.guard).filter(name=name).exists():
      raise ValidationError('해당 액션이미지가 이미 존재합니다.')
    return name
