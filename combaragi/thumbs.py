# -*- encoding: utf-8 -*-
"""
django-thumbs by Antonio Melé
http://django.es
"""
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from PIL import Image
from django.core.files.base import ContentFile
import cStringIO

def generate_thumb(img, thumb_size, format):
  """
  Generates a thumbnail image and returns a ContentFile object with the thumbnail
  
  Parameters:
  ===========
  img     File object
  
  thumb_size  desired thumbnail size, ie: (200,120)
  
  format    format of the original image ('jpeg','gif','png',...)
        (this format will be used for the generated thumbnail, too)
  """
  
  img.seek(0) # see http://code.djangoproject.com/ticket/8222 for details
  image = Image.open(img)

  # get size
  if type(thumb_size) == tuple:
    thumb_w, thumb_h = thumb_size
  else:
    if thumb_size > image.size[0]:
      (thumb_w, thumb_h) = image.size
    else:
      ratio = float(image.size[1]) / image.size[0]
      thumb_w = thumb_size
# adjust width and height to your needs
      thumb_h = int(ratio * thumb_w)

  # Convert to RGB if necessary
  if image.mode not in ('L', 'RGB'):
    image = image.convert('RGB')
    
  # If you want to generate a square thumbnail
  if thumb_w == thumb_h:
    # quad
    xsize, ysize = image.size
    # get minimum size
    minsize = min(xsize,ysize)
    # largest square possible in the image
    xnewsize = (xsize-minsize)/2
    ynewsize = (ysize-minsize)/2
    # crop it
    image2 = image.crop((xnewsize, ynewsize, xsize-xnewsize, ysize-ynewsize))
    # load is necessary after crop
    image2.load()
    # thumbnail of the cropped image (with ANTIALIAS to make it look better)
    image2.thumbnail((thumb_w, thumb_h), Image.ANTIALIAS)
  else:
    # not quad
    image2 = image
    image2.thumbnail((thumb_w, thumb_h), Image.ANTIALIAS)

  io = cStringIO.StringIO()
  # PNG and GIF are the same, JPG is JPEG
  if format.upper()=='JPG':
    format = 'JPEG'

  image2.save(io, format)
  return ContentFile(io.getvalue())

def get_thumb_url(split, size):
  if type(size) == int:
    return '%s.%s.%s' % (split[0],size,split[1])
  elif type(size) == tuple and len(size) == 2:
    return '%s.%sx%s.%s' % (split[0],size[0],size[1],split[1])
  return None

class ImageWithThumbsFieldFile(ImageFieldFile):
  """
  See ImageWithThumbsField for usage example
  """
  def __init__(self, *args, **kwargs):
    super(ImageWithThumbsFieldFile, self).__init__(*args, **kwargs)
    self.sizes = self.field.sizes
    
    if self.sizes:
      def get_size(self, size):
        if not self:
          return ''
        else:
          split = self.url.rsplit('.',1)
          return get_thumb_url(split, size)
          
      for size in self.sizes:
        if type(size) == int:
          setattr(self, 'url_%s' % size, get_size(self, size))
        elif type(size) == tuple and len(size) == 2:
          setattr(self, 'url_%sx%s' % size, get_size(self, size))
        
  def save(self, name, content, save=True):
    super(ImageWithThumbsFieldFile, self).save(name, content, save)
    
    if self.sizes:
      for size in self.sizes:
        split = self.path.rsplit('.',1)
        thumb_name = get_thumb_url(split, size)        
        
        # you can use another thumbnailing function if you like
        thumb_content = generate_thumb(content, size, split[1])
        
        thumb_name_ = self.storage.save(thumb_name, thumb_content)    
        
        #if not thumb_name == thumb_name_:
        #  raise ValueError('There is already a file named %s' % thumb_name)
    
  def delete(self, save=True):
    name=self.name
    super(ImageWithThumbsFieldFile, self).delete(save)
    if self.sizes:
      for size in self.sizes:
        split = name.rsplit('.',1)
        thumb_name = get_thumb_url(split, size)
        try:
          self.storage.delete(thumb_name)
        except:
          pass

            
class ImageWithThumbsField(ImageField):
  attr_class = ImageWithThumbsFieldFile
  """
  Usage example:
  ==============
  photo = ImageWithThumbsField(upload_to='images', sizes=((64, 64),(300),)
  
  To retrieve image URL, exactly the same way as with ImageField:
    my_object.photo.url
  To retrieve thumbnails URL's just add the size to it:
    my_object.photo.url_125x125
    my_object.photo.url_300x200
  
  Note: The 'sizes' attribute is not required. If you don't provide it, 
  ImageWithThumbsField will act as a normal ImageField
    
  How it works:
  =============
  For each size in the 'sizes' atribute of the field it generates a 
  thumbnail with that size and stores it following this format:
  
  available_filename.[width]x[height].extension

  Where 'available_filename' is the available filename returned by the storage
  backend for saving the original file.
  
  Following the usage example above: For storing a file called "photo.jpg" it saves:
  photo.jpg      (original file)
  photo.125x125.jpg  (first thumbnail)
  photo.300.jpg    (second thumbnail, ratio based)
  
  With the default storage backend if photo.jpg already exists it will use these filenames:
  photo_.jpg
  photo_.125x125.jpg
  photo_.300.jpg
  
  Note: django-thumbs assumes that if filename "any_filename.jpg" is available 
  filenames with this format "any_filename.[widht]x[height].jpg" will be available, too.
  
  To do:
  ======
  Add method to regenerate thubmnails
  
  """
  def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, sizes=None, **kwargs):
    self.verbose_name=verbose_name
    self.name=name
    self.width_field=width_field
    self.height_field=height_field
    self.sizes = sizes
    super(ImageField, self).__init__(**kwargs)

