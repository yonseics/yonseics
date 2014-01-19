# -*- coding: utf-8 -*-

__author__ = 'seung-giim'

from django import forms
from combaragi.bomb.models import Bomb

class BombCreateForm(forms.ModelForm):
    private = forms.BooleanField(
        label='비공개',
        help_text='폭탄을 비공개로 만듭니다.',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'no_overlabel':True}))
    bombfile = forms.FileField(label=u'파일', widget=forms.FileInput(attrs={'no_overlabel': True}))

    class Meta:
        model = Bomb
        exclude = ('user')
