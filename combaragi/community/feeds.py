# -*- coding: utf-8 -*-
# Author: UNKI
from django.conf import settings

from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from ccboard.models import Bulletin

class RssFeed(Feed):
  title = 'yonseics.net rss'
  link = 'http://yonseics.net'
  description = '연세대학교 컴퓨터과학과의 RSS Feed입니다.'

  def items(self):
    return Bulletin.bulletIns.filter(board__secret=False).order_by('-created')[:5]
  def item_link(self, item):
    return 'http://%s/board/%s/read/%s/'%(settings.DOMAIN_URL, item.board.name, item.id)
  def item_pubdate(self, item):
    return item.created
  def item_categories(self, item):
    if item.category:
      return item.category.title,
    else:
      return '',

class AtomFeed(RssFeed):
  feed_type = Atom1Feed
  title_template = 'feeds/rss_title.html'
  description_template = 'feeds/rss_description.html'

