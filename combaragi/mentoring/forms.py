# -*- coding: utf-8 -*-
# Author: UNKI

from django import forms
from django.db.models import Q
from mentoring.models import Relation
from ccboard.widgets import JQueryAutoComplete

class QuestionWriteForm(forms.Form):
  def __init__(self, request, *args, **kwargs):
    super(QuestionWriteForm, self).__init__(*args, **kwargs)
#self.fields['mentor'].queryset = Relation.objects.filter(mentee=request.user).exclude(mentor=request.user)
    self.fields['mentor'].queryset = Relation.objects.filter(Q(accepted=True, mentee=request.user), ~Q(mentor__user=request.user))

  mentor = forms.ModelChoiceField(queryset=Relation.objects.none(),
      required=True, empty_label='멘토를 선택해 주세요')
  title = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class':'inputContent'}))
  content = forms.CharField(required=True, widget=forms.Textarea(attrs={'class':'textareaContent', 'rows':'30'}))

class QuestionReplyForm(forms.Form):
  reply = forms.CharField(required=True, widget=forms.Textarea(attrs={'class':'textareaContent', 'rows':'30'}))

class SearchForm(forms.Form):
  def __init__(self, type, *args, **kwargs):
    super(SearchForm, self).__init__(*args, **kwargs)
    self.fields['key'].widget = JQueryAutoComplete(source='/mentoring/search/%s/' % type, options={
      'minChars': 0,
      'width': 310,
      }, attrs={'class':'input_text'})

  key=forms.CharField(label=u'제목검색', required=False)

class RegisterMentorForm(forms.Form):
  tags = forms.CharField(label=u'관심분야', max_length=40,
      help_text='멘토링 가능한 분야를 ,로 구분하여 적어주세요.',
      widget = JQueryAutoComplete(source='/mentoring/search/tags/', options={
        'minChars': 0,
        'width': 310,
        }, attrs={'class':'i_text'})
      )

#  student = forms.BooleanField(required=False)
#  company = forms.CharField(max_length=40, widget=forms.TextInput(attrs={'class':'i_text'}))

class RegisterMenteeForm(forms.Form):
  msg = forms.CharField(label=u'멘토요청 메시지', max_length=100,
      help_text='멘토를 요청하는 메시지를 100자 이내로 적어주세요.',
      widget=forms.TextInput(attrs={'class':'i_text'}))

