from django.contrib import admin
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
            self.fields = ('board', 'title', 'content', 'notice')
            self.exclude = None
        else:
            self.fields = None
            self.exclude = ('parent',)
        field_list = super(MyBulletinAdmin, self).get_fieldsets(request, obj)
        return field_list

admin.site.register(Bulletin, MyBulletinAdmin)
