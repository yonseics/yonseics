# -*- coding: utf-8 -*- 
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from community.models import UserProfile
# 해시 함수 사용을 위해
from hashlib import md5
from hashlib import sha224
from base64 import b64encode

def init(*args, **kwargs):
	# 테스트 유저를 만들어 줍니다
	try:
		try:
			user = User.objects.get(username='a')
		except:
			user = User.objects.create_user('a', 'a@combaragi.com', '1')
		UserProfile.objects.get_or_create(
								user=user,
								sid='0123456',
								sidHash=md5(b64encode(sha224('0123456').hexdigest())).hexdigest(),
								gender=u'M',
								status=u'Y',
								sendmail=True,
								)
		user.first_name='임승기'
		user.is_staff = True
		user.is_superuser = True
		user.save()
		try:
			user = User.objects.get(username='b')
		except:
			user = User.objects.create_user('b', 'a@combaragi.com', '1')
		UserProfile.objects.get_or_create(
								user=user,
								sid='0234567',
								sidHash=md5(b64encode(sha224('0234567').hexdigest())).hexdigest(),
								gender=u'F',
								status=u'G',
								sendmail=True,
								)
		user.first_name='이석준'
		user.is_staff = True
		user.is_superuser = True
		user.save()
		try:
			user = User.objects.get(username='c')
		except:
			user = User.objects.create_user('c', 'a@combaragi.com', '1')
		UserProfile.objects.get_or_create(
								user=user,
								sid='0345678',
								sidHash=md5(b64encode(sha224('0345678').hexdigest())).hexdigest(),
								gender=u'M',
								status=u'E',
								sendmail=True,
								)
		user.first_name='김동원'
		user.is_staff = True
		user.is_superuser = True
		user.save()
		try:
			user = User.objects.get(username='d')
		except:
			user = User.objects.create_user('d', 'a@combaragi.com', '1')
		UserProfile.objects.get_or_create(
								user=user,
								sid='0456789',
								sidHash=md5(b64encode(sha224('0456789').hexdigest())).hexdigest(),
								gender=u'F',
								status=u'Y',
								sendmail=True,
								)
		user.first_name='이태우'
		user.is_staff = True
		user.is_superuser = True
		user.save()
		print '테스트 유저 a, b, c, d가 만들어졌습니다 비밀번호는 1입니다.'
	except:
		print '테스트 유저 a, b, c, d가 이미 있습니다.'

class Command(BaseCommand):
	option_list = BaseCommand.option_list

	help = ('Create Test Users.')

	requires_model_validation = True
	can_import_settings = True

	def handle(self, *args, **options):
		return init(args, options)
