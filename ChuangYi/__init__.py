from django.core.exceptions import ValidationError

from django.forms import BooleanField


def to_python(self, value):
    if value in (True, 'True', 'true', '1'):
        return True
    elif value in (False, 'False', 'false', '0'):
        return False
    else:
        return None


def validate(self, value):
    if value is None and self.required:
        raise ValidationError(self.error_messages['required'], code='required')


BooleanField.to_python = to_python
BooleanField.validate = validate
