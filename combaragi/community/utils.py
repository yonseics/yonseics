# -*- coding: utf-8 -*-

from os import path
from datetime import datetime

# Bomb path
def get_bomb_file_path(instance, filename):
    return path.join('bomb', '%s' % instance.user.get_profile().sidHash, filename)

# 포토로그용 파일 path
def get_image_path(instance, filename): 
  return path.join('photologue', datetime.now().strftime("%Y_%m_%d"), filename)

# 초상화용 파일 path
def get_portrait_path(instance, filename): 
  ext = path.splitext(filename)[1]
  return path.join('portrait', '%s%s' % (instance.sidHash, ext))

# 파일 업로드용 파일 path
def get_upload_path(instance, filename): 
  return path.join('uploaded', datetime.now().strftime("%Y_%m_%d"), filename)
