from django.forms import ModelChoiceField, ModelMultipleChoiceField

class UserModelChoiceField(ModelChoiceField):
  def label_from_instance(self, obj):
    return obj.get_full_name()

class UserModelMultipleChoiceField(ModelMultipleChoiceField):
  def label_from_instance(self, obj):
    return obj.get_full_name()
