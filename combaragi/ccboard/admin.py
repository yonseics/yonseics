from django.contrib import admin
from django.db.models.query_utils import Q
from combaragi.ccboard.models import Board, Bulletin, RelatedPosition, RelatedFile, PhotoTag, Scrap, Category

admin.site.register(Board)
admin.site.register(RelatedPosition)
admin.site.register(RelatedFile)
admin.site.register(PhotoTag)
admin.site.register(Scrap)
admin.site.register(Category)

class MyBulletinAdmin(admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser:
            if obj and obj.isHiddenUser:
                self.fields = ('board', 'title', 'content', 'notice')
            else:
                self.fields = ('board', 'writer', 'title', 'content', 'notice')
            self.exclude = None
        else:
            self.fields = None
            self.exclude = ('parent',)
        field_list = super(MyBulletinAdmin, self).get_fieldsets(request, obj)
        return field_list

    def queryset(self, request):
        qs = super(MyBulletinAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            #Q(isHiddenUser=False) &
            #Q(deleted=False) &
            Q(board__secret=False) &
            Q(parent=None)
        )


admin.site.register(Bulletin, MyBulletinAdmin)
