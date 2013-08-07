"""
Tests for the multiple file upload widget and field.

Created by Edward Dale (www.scompt.com)
Released into the Public Domain
"""

from django.utils.datastructures import MultiValueDict
from django import forms
import unittest
from django.test.client import Client
from django.test import TestCase
from multifile import *

class MultiFileInputTest(unittest.TestCase):
  """
  Tests for the widget itself.
  """

  def testBasics(self):
    """
    Make sure the basics are correct (needs_multipart_form & is_hidden).
    """
    m=MultiFileInput()

    self.assertTrue(m.needs_multipart_form)
    self.assertFalse(m.is_hidden)

  def testNoRender(self):
    """
    Makes sure we show a minimum of 1 input box.
    """
    m=MultiFileInput({'count':0})
    r=m.render(name='blah', value='bla', attrs={'id':'test'})

    self.assert_('<input type="file" name="blah[]" id="test0" />' in r)

  def testSingleRender(self):
    """
    Test the output of a single field being rendered.
    """
    m=MultiFileInput()
    r=m.render(name='blah', value='bla', attrs={'id':'test'})

    self.assert_('<input type="file" name="blah[]" id="test0" />' in r)

  def testMultiRender(self):
    """
    Tests that two input boxes are rendered when given a count of 2.
    """
    m=MultiFileInput({'count':2})
    r=m.render(name='blah', value='bla', attrs={'id':'test'})

    self.assert_('<input type="file" name="blah[]" id="test0" />' in r)
    self.assert_('<input type="file" name="blah[]" id="test1" />' in r)

class MultiFileFieldTest(unittest.TestCase):
  """
  Tests that MultiFileField field.
  """

  class OptionalForm(forms.Form):
    """
    A simple Form that has an optional MultiFileField.
    """
    files = MultiFileField(required=False)

  class RequiredForm(forms.Form):
    """
    A simple Form that has an required MultiFileField.
    """
    files = MultiFileField(required=True)

  class MultiForm(forms.Form):
    """
    A simple Form with a MultiFileField with 2 input boxes.
    """
    files = MultiFileField(count=2)

  class StrictForm(forms.Form):
    files = MultiFileField(count=2, strict=True)

  def testOneRender(self):
    """
    Test the rendering of a MultiFileField with 1 input box.
    """
    f = self.RequiredForm()
    p=f.as_p()

    self.assert_('<input type="file" name="files[]" id="id_files0" />' in p)

  def testTwoRender(self):
    """
    Test the rendering of a MultiFileField with 2 input boxes.
    """
    f = self.MultiForm()
    p=f.as_p()

    self.assert_('<input type="file" name="files[]" id="id_files0" />' in p)
    self.assert_('<input type="file" name="files[]" id="id_files1" />' in p)

  def testNoFiles(self):
    """
    Tests binding a Form with required and optional MultiFileFields.
    """
    f = self.RequiredForm({}, {})
    self.assertTrue(f.is_bound)
    self.assertFalse(f.is_valid())

    f = self.OptionalForm({}, {})
    self.assertTrue(f.is_bound)
    self.assertTrue(f.is_valid())

  def testBind(self):
    """
    Tests the binding of the form.  Probably not necessary.
    """
    file_data = {'files': {'filename':'face.jpg', 'content': ''}}
    f = self.RequiredForm()
    self.assertFalse(f.is_bound)

    f = self.RequiredForm({}, file_data)
    self.assertTrue(f.is_bound)

class FixedMultiFileTest(unittest.TestCase):
  def testSingleRender(self):
    """
    Test the output of a single field being rendered.
    """
    m=FixedMultiFileInput()
    r=m.render(name='blah', value='bla', attrs={'id':'test'})

    self.assertEquals('<p class="left"><input type="file" name="blah[]" id="test0" /></p>\n', r)
