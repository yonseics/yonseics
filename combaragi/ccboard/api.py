# -*- coding: utf-8 -*-
# Author: KIMSHIN
from ccboard.models import Board, Bulletin
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

# EXAMPLE
# 게시글/댓글 정보: curl http://yonseics.net/api/bulletin/3/?format=json
# 게시판 정보: curl http://yonseics.net/api/board/3/?format=json

class LoginRequiredAuthorization(Authorization):
    """로그인만 했으면 읽을 수 있습니다."""
    def read_detail(self, object_list, bundle):
        # TO DO: 401 메세지 어떻게 할까요?
        return bundle.request.user.is_anonymous() == False

class BulletinResource(ModelResource):
    """게시물, 댓글 정보입니다."""
    class Meta:
        queryset = Bulletin.objects.all()
        resource_name = 'bulletin'
        excludes = ['writerIP'] # 필요없는 정보는 여기에 추가합니다.
        authorization = LoginRequiredAuthorization()

    def dehydrate(self, bundle):
        bulletin = Bulletin.objects.get(id=bundle.data['id'])
        bundle.data['writer'] = bulletin.get_pure_writer_name()
        return bundle

class BoardResource(ModelResource):
    """게시판 정보입니다."""
    class Meta:
        queryset = Board.objects.all()
        resources_name = 'board'
        excludes = ['staff', 'updated']
        authorization = LoginRequiredAuthorization()

    def dehydrate(self, bundle):
        """해당 게시판에 속한 게시물들의 정보를 추가했습니다."""
        bulletins = dict()
        board = Board.objects.get(id=bundle.data['id'])
        for bulletin in board.bulletin_set.all():
            bulletins[bulletin.id] = {'title': bulletin.title,
                                      'writer': bulletin.get_pure_writer_name(),
                                      'hits': bulletin.hits,
                                      'commentCnt': bulletin.commentCnt,
                                      'created': bulletin.created,
                                     } # 게시물에 대해 [더 필요한/필요없는] 정보 있다면 이곳을 수정
        bundle.data['bulletins'] = bulletins
        return bundle
