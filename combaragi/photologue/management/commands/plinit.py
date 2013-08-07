from django.core.management.base import BaseCommand#, CommandError
#from photologue.management.commands import get_response, create_photosize
#from photologue.models import PhotoEffect
from photologue.models import PhotoSize

class Command(BaseCommand):
	help = ('Prompts the user to set up the default photo sizes required by Photologue.')
	requires_model_validation = True
	can_import_settings = True

	def handle(self, *args, **kwargs):
		return init(*args, **kwargs)

def init(*args, **kwargs):
	'''msg = '\nPhotologue requires a specific photo size to display thumbnail previews in the Django admin application.\nWould you like to generate this size now? (yes, no):'
	if get_response(msg, lambda inp: inp == 'yes', False):
		admin_thumbnail = create_photosize('admin_thumbnail', width=100, height=75, crop=True, pre_cache=True)
		msg = 'Would you like to apply a sample enhancement effect to your admin thumbnails? (yes, no):'
		if get_response(msg, lambda inp: inp == 'yes', False):
			effect, created = PhotoEffect.objects.get_or_create(name='Enhance Thumbnail', description="Increases sharpness and contrast. Works well for smaller image sizes such as thumbnails.", contrast=1.2, sharpness=1.3)
			admin_thumbnail.effect = effect
			admin_thumbnail.save()
	msg = '\nPhotologue comes with a set of templates for setting up a complete photo gallery. These templates require you to define both a "thumbnail" and "display" size.\nWould you like to define them now? (yes, no):'
	if get_response(msg, lambda inp: inp == 'yes', False):
		thumbnail = create_photosize('thumbnail', width=100, height=75)
		display = create_photosize('display', width=400, increment_count=True)
		msg = 'Would you like to apply a sample reflection effect to your display images? (yes, no):'
		if get_response(msg, lambda inp: inp == 'yes', False):
			effect, created = PhotoEffect.objects.get_or_create(name='Display Reflection', description="Generates a reflection with a white background", reflection_size=0.4)
			display.effect = effect
			display.save()'''
	create_photosize_by_set('thumbnail', width=75, height=75, crop=True, pre_cache=True)
	create_photosize_by_set('display', width=550, height=450, pre_cache=True)

def create_photosize_by_set(name, width=0, height=0, crop=False, pre_cache=False, increment_count=False):
	try:
		size = PhotoSize.objects.get(name=name)
		print 'photo size "%s" is already exist.' % name
	except PhotoSize.DoesNotExist:
		size = PhotoSize(name=name)
	print 'We will now define the "%s" photo size:' % size
	size.width = width
	size.height = height
	size.crop = crop
	size.pre_cache = pre_cache
	size.increment_count = increment_count
	size.save()
	print 'A "%s" photo size has been created.\n' % name
	return size
