Installation
------------

Put the rendertext app somewhere in your Python path, e.g. if you have
/home/django that you use to store your sites, you could put it
there. Then add 'rendertext' to INSTALLED_APPS in settings.py. Of
course, you could also put it directly in a site and add
'mysite.rendertext' to INSTALLED_APPS.

Then you just need to add the dictionary RENDERTEXT_FONTMAP which
specifies what a given font name resolves to. For instance:

  RENDERTEXT_FONTMAP = {
    'grunge': '/home/django/mysite/fonts/grunge.ttf'
  }
  
Put it in settings.py too. Rendertext uses Python Imaging Library so
you need to have that installed with the right font support.

You can also add RENDERTEXT_DIR to specify the directory under media
root in which the image files are put (default is 'rendertext/').

RENDERTEXT_OUTPUT_FORMAT determines the output format, either 'png'
(default) or 'gif'.


Usage
-----

To show text with a custom font, first load the tag library with
{% load rendertext %} and then pass the text through the rendertext
filter:

  {{ page.title|rendertext:"jiffy" }}

Similarly for string literals:

  {{ "Hello there!"|rendertext:"jiffy" }}

You can specify size, color and rotation too. Size 18:

  {{ "Hello there!"|rendertext:"jiffy,18" }}

Color is specified with a standard CSS specification. So you can get
green text with:

  {{ "Hello there!"|rendertext:"jiffy,18,#00ff00" }}

Rotation is specified as degrees to rotate counter-clockwise:

  {{ "Hello there!"|rendertext:"jiffy,18,#00ff00,90" }}

You can also specify the background color (if needed) with the last
parameter, like this:
  
  {{ "Hello there!"|rendertext:"jiffy,18,#00ff00,90,#000000" }}

The template filter produces an <img> tag like this:

  <img src="/sitemedia/rendertext/41f97f2c80e9c581c9fa85ca4efda8d9.png" alt="Hello there!" width="120" height="61" />


Note that rendertext by default spits out PNGs with transparency. To
show these properly in IE 5.5+ and 6, you need to apply the Javascript
IE PNG hack (if you're using jQuery, there's a plugin for this).
Another option is to turn on GIF output with
RENDERTEXT_OUTPUT_FORMAT='gif' in your settings.py. Since the
transparency support in GIF is rather lousy, you may need to change
the background color used to antialias the images to match the
background color of your page. By default rendertext uses a white
background for GIFs.

Also note that the font renderer in PIL is a bit buggy with some
fonts, especially the large and curvy ones. If some snippets are
mysteriously cut off to the right, try adding a space or two after the
string and see if it helps. This is easiest to do with a custom
template filter as described below.

If you change the font file or something similar that the caching
mechanism in rendertext is not clever enough to detect, you can simply
delete the generated files. They will then be regenerated. The caching
mechanism doesn't use the database, it only looks at what's available
in the file system.


Custom template filter
----------------------

In accordance with the DRY principle, I suggest you write a custom
template filter if you find yourself specifying the same parameters to
rendertext in several templates. Here's a recipe.

Create a subdirectory 'templatetags' in your site directory at the
same level as models.py and views.py. Put an empty __init__.py file in
there and add your custom file, e.g. 'renderheaders.py'. You should
have something like this:

  models.py
  views.py
  templatetags/
      __init__.py
      renderheaders.py

Then put something like this in renderheaders.py:

  from django import template

  register = template.Library()

  from rendertext.templatetags.rendertext import render_tag

  @register.filter
  def renderjiffyheader(text):
      text = unicode(text)
      return render_tag(text, "jiffy", 20, "#881b1e")

Then put in a {% load renderheaders %} in your template, and you can
now write {{ myvar|renderjiffyheader }}.

If the font renderer is a bit buggy, you could add a space by
replacing the last line with:

      return render_tag(text + " ", "jiffy", 20, "#881b1e")

The function render_tag takes the same parameters as the rendertext
filter but as normal function parameters instead of the
comma-separated string.
