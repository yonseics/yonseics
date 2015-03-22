# -*- coding: utf-8 -*-
__author__ = 'unki'
from PIL import Image
from os import path as os_path
from re import compile as re_compile
from re import findall as re_findall
from re import IGNORECASE as re_IGNORECASE

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

def unique(inlist, keepstr=True):
  typ = type(inlist)
  if not typ == list:
    inlist = list(inlist)
  i = 0
  while i < len(inlist):
    try:
      del inlist[inlist.index(inlist[i], i + 1)]
    except:
      i += 1
  if not typ in (str, unicode):
    inlist = typ(inlist)
  else:
    if keepstr:
      inlist = ''.join(inlist)
  return inlist

# XSS 공격 방지
def stripXSS(str):
  str = re_compile(r'<style', re_IGNORECASE).sub('&lt;style', str)
  str = re_compile(r'</style', re_IGNORECASE).sub('&lt;/style', str)
  str = re_compile(r'<script', re_IGNORECASE).sub('&lt;script', str)
  str = re_compile(r'</script', re_IGNORECASE).sub('&lt;/script', str)
  str = re_compile(r'<iframe', re_IGNORECASE).sub('&lt;iframe', str)
  str = re_compile(r'</iframe', re_IGNORECASE).sub('&lt;/iframe', str)
  # on 시리즈를 다 막고, 안 바뀔 때까지 계속 바꾸자
  prestr = None
  while prestr != str:
    prestr = str
    str = re_compile(r'<(.*)on(\w+)=(.*)>', re_IGNORECASE).sub(r'<\1no\2=\3>', str)
  str = re_compile(r'javascript:', re_IGNORECASE).sub(r'noscript:', str)
  str = re_compile(r'vbscript:', re_IGNORECASE).sub(r'noscript:', str)
  str = re_compile(r'behavior:', re_IGNORECASE).sub(r'noscript:', str)
  str = re_compile(r'<meta', re_IGNORECASE).sub('&lt;meta', str)
  str = re_compile(r'<?xml:', re_IGNORECASE).sub('&lt;?xml:', str)
  str = re_compile(r'<xml', re_IGNORECASE).sub('&lt;xml', str)
  str = re_compile(r'<link', re_IGNORECASE).sub('&lt;link', str)
  str = re_compile(r'<layer', re_IGNORECASE).sub('&lt;layer', str)
  str = re_compile(r'AllowScriptAccess=', re_IGNORECASE).sub('AllowScriptAccess="never" ', str)
  #str = re_compile(r'<object', re_IGNORECASE).sub('&lt;object', str)
  str = re_compile(r'<?import', re_IGNORECASE).sub('&lt;?import', str)
  str = re_compile(r'eval\(', re_IGNORECASE).sub('noeval\(', str)

  return str

# tval로 CSRF공격인지 확인합니다.
@login_required
def checkCSRF_with_tval(request):
  tval = int(request.GET.get('tval', 0))
  if tval is 0:
    # 수상한 짓을 하려고 했습니다.
    return True
  return request.user.get_profile().get_tval() != tval

# CSRF공격으로 간주되는 행동을 캐치합니다.
@login_required
def dealCSRF(request):
  return render_to_response('noExist.html',{'user':request.user, 'target':'메롱. CSRF공격 권한이'})

def CompleteHTML(html):
  # 1. Close every unclosed tags. e.g., <a
  bracket_cnt = 0
  brackets = re_findall('[<>]', html)
  is_in_pre_tag = False
  previous_6 = ''
  for c in html:
    if not is_in_pre_tag:
      if c == '<':
        bracket_cnt += 1
      elif c == '>':
        bracket_cnt -= 1
    previous_6 = (previous_6 + c)[-6:]
    if previous_6.endswith('<pre>'):
      is_in_pre_tag = True
    if previous_6.endswith('</pre>'):
      is_in_pre_tag = False
  html += '>' * bracket_cnt
  
  # 2. Close every unmatched tags. e.g., <a href="...">
  stk = []
  is_in_pre_tag = False
  tags = [str[1:-1] for str in re_findall('<\/?\w+[\'\"a-zA-Z\.\=\ ]*>', html)]
  for tag in tags:
    if tag == 'pre':
      is_in_pre_tag = True
    elif tag == '/pre':
      is_in_pre_tag = False
    if is_in_pre_tag:
      continue
    if tag[0] != '/':
      stk.append(tag.split()[0].split('>')[0])
    elif tag[0] == '/' and len(stk) and stk[-1] == tag[1:]:
      stk.pop()
    else:
      pass
  stk.reverse()
  return html + ''.join(['</%s>' % tagname for tagname in stk])

def resize_image(path, width):
# open an image file (.bmp,.jpg,.png,.gif) you have in the working folder
  fileName, fileExtension = os_path.splitext(path)
  image = Image.open(path)
  if width > image.size[0]:
    return
  ratio = float(image.size[1]) / image.size[0]
# adjust width and height to your needs
  height = ratio * width
# use one of these filter options to resize the image
  resized = image.resize((width, height), Image.ANTIALIAS)    # best down-sizing filter
  image.save(path + '_bak')
  resized.save(path)
