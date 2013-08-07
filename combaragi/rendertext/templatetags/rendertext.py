from django import template

register = template.Library()

import md5, os
import Image, ImageFont, ImageDraw, ImageColor
from django.conf import settings

## def generate_palette(bg_color, fg_color):
##     colors = 256
##     palette = []
##     for j in range(0, colors):
##         for i in range(0,3):
##             palette.append(int(bg_color[i] + j / (colors - 1.0) * (fg_color[i] - bg_color[i])))

##     return palette

def render(text, fontalias, size = 12, color = "#000", rotation = 0, bg_color = None):
    """Construct image from text.

    Returns a tuple with the image file path, width and height. Takes
    the parameters 'fontalias', 'size' (default 12), 'color' (default
    black) as CSS hex string, 'rotation' (default 0) which is the
    degrees to rotate the text counter-clockwise, and lastly
    'bg_color' (mostly useful when in GIF mode).

    The constructed image is stored in a cache under the media root in
    the RENDERTEXT_DIR set in settings.py (default is 'rendertext/').
    The font file to use is determined by mapping the fontalias
    through the RENDERTEXT_FONTMAP setting, a dictionary from
    fontalias strings to font file paths, e.g. {'verdana':
    '/home/django/fonts/verdana.ttf'}. RENDERTEXT_OUTPUT_FORMAT
    determines the output file format, either 'png' (default) or 'gif'."""

    # get settings
    render_dir = "rendertext/"
    if hasattr(settings, "RENDERTEXT_DIR"):
        render_dir = settings.RENDERTEXT_DIR

    fontmap = settings.RENDERTEXT_FONTMAP
    fontfile = fontmap[fontalias]

    gifmode = False
    if hasattr(settings, "RENDERTEXT_OUTPUT_FORMAT"):
        gifmode = settings.RENDERTEXT_OUTPUT_FORMAT == 'gif'

    # file path
    info = "|".join([text, fontalias, str(size), str(color), str(rotation)])
    name = md5.new(info.encode('utf-8')).hexdigest()
    
    extension = ".png"
    if gifmode:
        extension = ".gif"
    
    filepath = render_dir + name + extension

    # colors
    fg_color = ImageColor.getrgb(color)
    if not bg_color:
        if gifmode:
            bg_color = (255, 255, 255)
        else:
            bg_color = fg_color
    
    dim = (-1, -1)
    if not os.access(settings.MEDIA_ROOT + filepath, os.F_OK):
        # construct the image
        imf = ImageFont.truetype(fontfile, size)
        dim = imf.getsize(text)
        im = Image.new("RGBA", (dim[0]+1,dim[1]), bg_color + (0,))

        draw = ImageDraw.Draw(im)
        weird_font_renderer_fix = " "
        draw.text((1, 0), text + weird_font_renderer_fix, font=imf, fill=fg_color)

        if rotation:
            if rotation == 90:
                im = im.transpose(Image.ROTATE_90)
            elif rotation == 180:
                im = im.transpose(Image.ROTATE_180)
            elif rotation == 270:
                im = im.transpose(Image.ROTATE_270)
            else:
                im = im.rotate(rotation, Image.BICUBIC, True)
            dim = im.size

        if not os.access(settings.MEDIA_ROOT + render_dir, os.F_OK):
            os.makedirs(settings.MEDIA_ROOT + render_dir)

        if gifmode:
            # unfortunately, PIL support for palette mode is rather
            # flaky so we have to hack it a bit

            oldim = im
            im = im.convert('P', dither=Image.NONE)

            # locate a good background color index
            hist = im.histogram()
            min_val = 1000000
            index = 0
            for i in range(0, len(hist)):
                if hist[i] < min_val:
                    min_val = hist[i]
                    index = i
                    if min_val == 0:
                        break

            # patch any fully transparent pixels
            src = oldim.load()
            dest = im.load()
            for y in range(0, dim[1]):
                for x in range(0, dim[0]):
                    if src[x, y][3] == 0:
                        dest[x, y] = index

            im.save(settings.MEDIA_ROOT + filepath, "GIF", transparency = index)
        else:
            im.save(settings.MEDIA_ROOT + filepath, "PNG")
            
    else:
        # read width and height
        im = Image.open(settings.MEDIA_ROOT + filepath)
        dim = im.size

    return (settings.MEDIA_URL + filepath, dim[0], dim[1])
    

def render_tag(text, *args, **kwargs):
    return text
    """Construct image tag from text."""
    (path, width, height) = render(text, *args, **kwargs)
    if not path:
        return ""
    else:
        dim = ""
        if width > 0 and height > 0:
            dim = 'width="%s" height="%s" ' % (width, height)
            
        #return '<img src="%s" alt="%s" %s/><span style="visibility:hidden;">&nbsp;</span>' % (path, text, dim)
        return '<img src="%s" alt="%s" %s/>' % (path, text, dim)

@register.filter
def rendertext(text, args):
    """Construct and return image tag from text.

    Takes the parameters 'fontalias', 'size' (default 12), 'color'
    (default black) as CSS hex string, 'rotation' (default 0) which is
    the degrees to rotate the text counter-clockwise, and lastly
    'bg_color' (mostly useful when in GIF mode).

    The constructed image is stored in a cache under the media root in
    the RENDERTEXT_DIR set in settings.py (default is 'rendertext/').
    The font file to use is determined by mapping the fontalias
    through the RENDERTEXT_FONTMAP setting, a dictionary from
    fontalias strings to font file paths, e.g. {'verdana':
    '/home/django/fonts/verdana.ttf'}. RENDERTEXT_OUTPUT_FORMAT
    determines the output file format, either 'png' (default) or 'gif'."""

    # get arguments
    text = unicode(text)
    fontalias = ""
    size = 12
    color = "#000"
    rotation = 0
    
    args_t = args.split(",")
    try:
        fontalias = args_t[0]
        size = int(args_t[1])
        color = args_t[2]
        rotation = int(args_t[3])
    except:
        # simply ignore errors
        pass
        
    return render_tag(text, fontalias, size, color, rotation)
rendertext.is_safe = True

@register.filter
def render_black(text, args):
  text = unicode(text)
  return render_tag(text, "ygo120", int(args), "black")
render_black.is_safe = True

@register.filter
def render_bold_black(text, args):
  text = unicode(text)
  return render_tag(text, "ygo140", int(args), "black")
render_bold_black.is_safe = True

@register.filter
def render_sharp_black(text, args):
  text = unicode(text)
  return render_tag(text, "ygo110", int(args), "black")
render_sharp_black.is_safe = True

@register.filter
def render_white(text, args):
  text = unicode(text)
  return render_tag(text, "ygo140", int(args), "white")
render_white.is_safe = True

@register.filter
def render_red(text, args):
  text = unicode(text)
  return render_tag(text, "ygo130", int(args), "red")
render_red.is_safe = True

@register.filter
def render_cyan(text, args):
  text = unicode(text)
  return render_tag(text, "ygo120", int(args), "#2FA694")
render_cyan.is_safe = True

@register.filter
def render_grey(text, args):
  text = unicode(text)
  return render_tag(text, "ygo140", int(args), "#CACACA")
render_grey.is_safe = True

@register.filter
def render_darkgrey(text, args):
  text = unicode(text)
  return render_tag(text, "ygo140", int(args), "#B3B4B4")
render_darkgrey.is_safe = True


############################# purpose ############################

@register.filter
def render_button(text):
  text = unicode(text)
  return render_tag(text, "ygo140", 13, "#666")
render_button.is_safe = True

@register.filter
def render_form(text):
  text = unicode(text)
  return render_tag(text, "ygo140", 16, "#B3B4B4")
render_form.is_safe = True

@register.filter
def render_sid(text, args):
  text = unicode(text)
  return render_tag(text, "ygo140", int(args), '#%X' % ((967329 * int(text) + 4199429) % 0xFFFFFF))
render_sid.is_safe = True

@register.filter
def render_bread(text):
  text = unicode(text)
  return render_tag(text, "ygo130", 12, "#2FA694")
render_bread.is_safe = True

@register.filter
def render_head(text):
  text = unicode(text)
  return render_tag(text, "ygo130", 24, "black")
render_head.is_safe = True

@register.filter
def render_headlet(text):
  text = unicode(text)
  return render_tag(text, "ygo130", 18, "#3d3d3d")
render_headlet.is_safe = True

@register.filter
def render_ribbon(text):
  text = unicode(text)
  return render_tag(text, "ygo140", 18, "#CDCDCD")
render_ribbon.is_safe = True

@register.filter
def render_ribbon_mini(text):
  text = unicode(text)
  return render_tag(text, "ygo140", 13, "#dDdDdD")
render_ribbon_mini.is_safe = True

