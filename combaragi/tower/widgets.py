# -*- coding: utf-8 -*-
# widgets.py

from django import forms
from django.forms.widgets import flatatt
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.simplejson import JSONEncoder

class MultipleInputOutput(forms.TextInput):
  def __init__(self, *args, **kwargs):
    super(MultipleInputOutput, self).__init__(*args, **kwargs)

  def render_js(self, field_id):
    return u'''
    function add_input_output() {
      $(\'#more_io_field\').append($(\'<div>\' +
        \'<textarea id="id_%(id)s_in"></textarea>\' +
        \'<textarea id="id_%(id)s_out"></textarea></div>\'));
      var count = parseInt($(\'#%(id)s\').val());
      count++;
      $(\'#id_%(id)s_in\').attr(\'name\', \'%(id)s_in_\'+count);
      $(\'#id_%(id)s_in\').attr(\'id\', \'%(id)s_in_\'+count);
      $(\'#id_%(id)s_out\').attr(\'name\', \'%(id)s_out_\'+count);
      $(\'#id_%(id)s_out\').attr(\'id\', \'%(id)s_out_\'+count);
      $(\'#%(id)s\').val(count);
    }
    ''' % {'id': field_id}

  def render(self, name, value=None, attrs=None):
    final_attrs = self.build_attrs(attrs, name=name)
    if value:
      final_attrs['value'] = escape(smart_unicode(value))

    if not self.attrs.has_key('id'):
      final_attrs['id'] = 'id_%s' % name

    return u'''<div id="more_io_field" %(attrs)s></div>
    <span class="btn_pack medium icon"><span class="add"></span><a href="javascript:add_input_output();">추가</a></span>
    <input type="hidden" id="id_%(name)s" name="%(name)s" value=0>
    <script type="text/javascript"><!--//
    %(js)s//--></script>
    ''' % {
      'attrs' : flatatt(final_attrs),
      'js' : self.render_js(final_attrs['id']),
      'name' : name,
    }


