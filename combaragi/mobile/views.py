# -*- coding: utf-8 -*-
# Author: UNKI
from django.views.generic.simple import direct_to_template

def main_page(request):
  return direct_to_template(request, "mobile/index.html")