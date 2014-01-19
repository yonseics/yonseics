# -*- coding: utf-8 -*-
from django.template.defaultfilters import filesizeformat

__author__ = 'seung-giim'

from django import forms
from combaragi.bomb.models import Bomb

class BombCreateForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(BombCreateForm, self).__init__(*args, **kwargs)

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

    def clean(self):
        bombfile = self.cleaned_data['bombfile']
        if not Bomb.isUploadable(self.user, bombfile):
            remaining = Bomb.getMyRemaining(self.user)
            msg = u'개인 폭탄함이 꽉 차서 더 이상 업로드 할 수 없습니다. 남은용량: %s, 파일크기: %s' % (
                filesizeformat(remaining),
                filesizeformat(bombfile.size)
            )
            raise forms.ValidationError(msg)
        return self.cleaned_data
