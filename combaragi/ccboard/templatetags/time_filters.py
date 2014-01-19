# -*- coding: utf-8 -*-

from django import template
register = template.Library()

@register.filter(name='humanizeTimeDiff')
def humanizeTimeDiff(timestamp = None):
  """
  Returns a humanized string representing time difference
  between now() and the input timestamp.

  The output rounds up to days, hours, minutes, or seconds.
  4 days 5 hours returns '4 days'
  0 days 4 hours 3 minutes returns '4 hours', etc...
  """
  from datetime import datetime

  now = datetime.now()
  reverse = now < timestamp
  if not reverse:
    timeDiff = now - timestamp
  else:
    timeDiff = timestamp - now
  years = timeDiff.days/365
  months = timeDiff.days%365/30
  days = timeDiff.days%365%30
  hours = timeDiff.seconds/3600
  minutes = timeDiff.seconds%3600/60
  seconds = timeDiff.seconds%3600%60

  if not reverse:
    str = u"%s %s전"
  else:
    str = u"%s %s후"
  if years > 0:
    str = str %(years, u"년")
    return str
  elif months > 0:
    str = str %(months, u"달")
    return str
  elif days > 0:
    str = str %(days, u"일")
    return str
  elif hours > 0:
    str = str %(hours, u"시간")
    return str
  elif minutes > 0:
    str = str %(minutes, u"분")
    return str
  elif seconds > 0:
    str = str %(seconds, u"초")
    return str
  else:
    return u"방금전"
