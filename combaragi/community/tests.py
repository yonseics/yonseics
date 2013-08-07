# -*- coding: utf-8 -*-
# Author: UNKI

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from community.models import UserProfile

# 해시 함수 사용을 위해
from hashlib import md5
from hashlib import sha224
from base64 import b64encode

from combaragi import utils


class UtilTest(TestCase):
  def test_CompleteHTML(self):
    """
    Tests CompleteHTML
    """
    # Complete unfinished tags
    self.assertEqual(utils.CompleteHTML('<a'), '<a></a>')
    self.assertEqual(utils.CompleteHTML('<a b'), '<a b></a>')
    # Complete unmatched tags
    self.assertEqual(utils.CompleteHTML('<a>'), '<a></a>')
    self.assertEqual(utils.CompleteHTML('<a href="naver.com">'), '<a href="naver.com"></a>')
    self.assertEqual(utils.CompleteHTML('<a href="naver.com">asdf'), '<a href="naver.com">asdf</a>')
    self.assertEqual(utils.CompleteHTML('<a>123'), '<a>123</a>')
    self.assertEqual(utils.CompleteHTML(''), '')
    self.assertEqual(utils.CompleteHTML('<a><b>123</a>'), '<a><b>123</a></b></a>')
    self.assertEqual(utils.CompleteHTML('<b><a>123</a>'), '<b><a>123</a></b>')


class BasicUserTest(TestCase):
  def setUp(self):
    user=User.objects.create_user(      # 여기서 유저 정보를 넣어 줍니다.
      username = 'unki',
      password = 'unki',
      email = 'limsungkee@gmail.com',
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
    sid = '0441003'
    UserProfile.objects.create(
      user=user,
      sid=sid,
      sidHash=md5(b64encode(sha224(sid).hexdigest())).hexdigest(),
      gender=u'M',
      status=u'Y',
    )
    self.user = user
  def test_user(self):
    self.assertTrue(self.user == self.user.get_profile().user)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

