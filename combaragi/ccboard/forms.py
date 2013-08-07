# -*- coding: utf-8 -*-
# Author: UNKI

from django import forms
from ccboard.models import Category, Bulletin
from ccboard.widgets import JQueryAutoComplete
from ccboard.multifile import MultiFileField
from os import path
from rendertext.templatetags.rendertext import render_button

NAME_CHOICES = (
  (u'실명', u'실명'),
  #(u'N', u'별명'),
  (u'익명', u'익명'),
)

class BulletinSearchForm(forms.Form):
  def __init__(self, boardname, *args, **kwargs):
    super(BulletinSearchForm, self).__init__(*args, **kwargs)
    #self.fields['key'].widget = JQueryAutoComplete(source='/board/qSearch/%s/'%boardname, options={
    #  'minChars': 0,
    #  'width': 310,
    #  }, attrs={'class':'input_text'})
  key=forms.CharField(label=u'제목검색', required=False, widget=forms.TextInput(attrs={'class':'input_text ac_input'}))

class UserSearchForm(forms.Form):
  key=forms.CharField(label=u'제목검색', max_length=20, widget=JQueryAutoComplete(source='/board/uSearch', options={
    'minChars': 0,
    'width': 140,
    }, attrs={'class':'input_text'}), required=True)

class WriteAndModifyForm(forms.Form):
  def __init__(self, board, *args, **kwargs):
    super(WriteAndModifyForm, self).__init__(*args, **kwargs)
    self.board = board
    #self.fields["category"].queryset = Category.objects.filter(board=board)
  file = MultiFileField(label=u'', required=False)
  position = forms.CharField(max_length=15, label=u'', widget=forms.TextInput(attrs={'readonly':'true'}), required=False,
    help_text=u'%s %s %s'%(
      u'<button class="btn" type="button" onclick="getPosition(\'id_position\');">%s</button><span id="pos_del_btn">' % render_button(u'위치지정'),
      u'<button class="btn" type="button" onclick="showPosition(\'id_position\');">%s</button>' % render_button(u'위치확인'),
      u'<button class="btn" type="button" onclick="deletePosition(\'id_position\');">%s</button></span>' % render_button(u'위치삭제')))      # 관련장소
  positionTitle = forms.CharField(max_length=40, label=u'첨부위치메모', required=False, widget=forms.TextInput(attrs={'class':'inputContent'}))
  gallery = forms.FileField(label=u'사진첩', help_text=u'[이미지 압축 파일(.zip)]', widget=forms.FileInput(attrs={'no_overlabel': True}), required=False)
  #category = forms.ModelChoiceField(queryset=None, label='카테고리', required=False, empty_label='카테고리 없음')
  title = forms.CharField(max_length=24, required=True, label=u'제목', widget=forms.TextInput(attrs={'size':60}))
  content = forms.CharField(required=True, label=u'내용',
                            help_text='code: &lt;pre&gt;#include...&lt;/pre&gt;',
                            widget=forms.Textarea(attrs={'class':'textareaContent', 'rows':'20'}))
  nametype = forms.BooleanField(label='익명글', required=False,
                                widget=forms.CheckboxInput(attrs={'no_overlabel':True}))  # 이름을 표시하는 방법 체크하면 익명
  notice = forms.BooleanField(label=u'공지글', required=False,
                              widget=forms.CheckboxInput(attrs={'no_overlabel':True}))
  #starpoint = forms.IntegerField(required=False, initial=0)
  def clean_nametype(self):
    if 'nametype' in self.cleaned_data:      # 만약 nametype이 올바른 값이면
      nametype = self.cleaned_data['nametype']
      if self.board.allowAnom or nametype == False:
        return nametype
    raise forms.ValidationError('수상한 짓을 하려고 했습니다.')
  def clean_gallery(self):
    # 여기서 압축파일이 zip인지 확인...
    if 'gallery' in self.cleaned_data and self.cleaned_data['gallery']:
      if path.splitext(self.cleaned_data['gallery'].name)[1] == '.zip':
        return self.cleaned_data['gallery']
      raise forms.ValidationError(u'올바른 zip 압축 파일이 아닙니다.')

class CommentForm(forms.Form):
  def __init__(self, board, bulletin, user, *args, **kwargs):
    self.board = board
    self.bulletin = bulletin
    self.user = user
    super(CommentForm, self).__init__(*args, **kwargs)
  content = forms.CharField(required=True, widget=forms.Textarea(attrs={'class':'textareaContent', 'rows':'10'}))
  #nametype = forms.ChoiceField(widget=forms.RadioSelect, label='이름을 표시할 때', choices=NAME_CHOICES)  # 이름을 표시하는 방법
  nametype = forms.BooleanField(label='익명', help_text=u'익명으로 댓글을 답니다.', required=False)  # 이름을 표시하는 방법 체크하면 익명
  #secret = forms.BooleanField(label=u'비밀', help_text=u'글쓴이만 볼 수 있습니다', required=False)
  starpoint = forms.IntegerField(initial=0, required=False)
  def clean_nametype(self):
    if 'nametype' in self.cleaned_data:      # 만약 nametype이 올바른 값이면
      nametype = self.cleaned_data['nametype']
      if self.board.allowAnom or nametype == False:
        return nametype
    raise forms.ValidationError('수상한 짓을 하려고 했습니다.')

  def clean(self):
    if self.bulletin.my_comments.exists():
      lastComment = self.bulletin.my_comments.all().order_by('-created')[0]
      if lastComment.content == self.cleaned_data['content'] and self.user == lastComment.writer:
        raise forms.ValidationError(u'이전 댓글과 내용이 동일합니다.')
    return self.cleaned_data

class AjaxCommentForm(forms.Form):
  content = forms.CharField(required=True)
