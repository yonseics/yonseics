# -*- coding: utf-8 -*-
from django.template.defaultfilters import linebreaksbr, escape

__author__ = 'unki'

from re import split as re_split

from django import template
register = template.Library()

@register.filter(name='linebreaksbrpre')
def linebreaksbrpre(str):
  # pre부분만 빼고...전부 바꿔주자.
  splited = re_split('</pre>',str)
  # 맨 마지막꺼 빼고 앞부분은 전부 <pre가 있는거렷다.
  lastStr = splited.pop()
  ret = []
  for splited_str in splited:
    # 여기서 앞부분것들만 pre에 적용을 안 받는 녀석들이다.
    pre_splited = re_split('<pre',splited_str)
    ret.append(linebreaksbr(pre_splited[0]))
    ret.append("<pre")
    if (len(pre_splited) > 1):
      split_content = pre_splited[1].split('>', 1)
    ret.append(split_content[0])  # <pre ~~~> 뒷부분
    ret.append('>')
    if (len(split_content) > 1):
      ret.append(split_content[1].replace("<", "&lt;").replace('>', '&gt;'))  # <pre>~~~</pre> 내용
    ret.append("</pre>")
  ret.append(linebreaksbr(lastStr))
  return "".join(ret)
