from combaragi.community.models import CurrentAdmin, UserProfile

VERSION = (0, 10)

if not CurrentAdmin.objects.exists():
    CurrentAdmin.objects.create(user=UserProfile.objects.get(pk=1).user)
