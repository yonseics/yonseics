from django.contrib import admin
from combaragi.ccboard.models import Board, Bulletin, RelatedPosition, RelatedFile, PhotoTag, Scrap, Category

admin.site.register(Board)
admin.site.register(Bulletin)
admin.site.register(RelatedPosition)
admin.site.register(RelatedFile)
admin.site.register(PhotoTag)
admin.site.register(Scrap)
admin.site.register(Category)
