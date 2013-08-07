from django.contrib import admin
from combaragi.community.models import UserProfile, Memo, PointLog, Emblem, Feed, BlackList

admin.site.register(UserProfile)
admin.site.register(Memo)
admin.site.register(PointLog)
admin.site.register(Emblem)
admin.site.register(Feed)
admin.site.register(BlackList)

