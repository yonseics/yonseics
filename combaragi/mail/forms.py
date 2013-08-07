# -*- coding: utf-8 -*-
# Author: UNKI

from django import forms

class MailSendForm(forms.Form):
  TARGET_CHOICE = (
    (0, u'내 동기들에게'),
    (1, u'전체메일'),
    (2, u'자신에게(Test)'),
  )
  target = forms.ChoiceField(required=True, choices=TARGET_CHOICE)
  subject = forms.CharField(required=True, label='제목', widget=forms.TextInput(attrs={'class':'textInput'}))
  content = forms.CharField(required=True, label='내용', widget=forms.Textarea(attrs={'class':'textLongInput', 'rows':'15'}))
