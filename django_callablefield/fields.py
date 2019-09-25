from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .values import A, B


from django.forms.fields import TypedChoiceField


class Fake:
    def __init__(self, repr):
        self.repr = repr
    def __repr__(self):
        return f'Fake({self.repr})'


A = Fake('A')
B = Fake('B')


class ABField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        kwargs['choices'] = [
            ('a', _('A')),
            ('b', _('B')),
        ]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["choices"]
        return name, path, args, kwargs

    def _parse_ab(self, value):
        if value == 'a':
            return A
        elif value == 'b':
            return B
        raise ValidationError('Invalid value for parsing.')

    def get_internal_type(self):
        return 'CharField'

    def from_db_value(self, value):
        print(f'from_db_value: {value}')
        # if value is None:
        #     return value
        return self._parse_ab(value)

    def to_python(self, value):
        print(f'to_python: {value}')
        if value in [A, B]:
            return value
        # elif value is None:
        #     return value
        return self._parse_ab(value)

    def get_prep_value(self, value):
        print(f'get_prep_value: {value}')
        print(f'value is A: {value is A}')
        print(f'value is B: {value is B}')
        print(f'value == A: {value == A}')
        print(f'value == B: {value == B}')
        if value is A:
            return 'a'
        elif value is B:
            return 'b'
        elif isinstance(value, str):
            return value
        raise Exception(f'in get_prep_value for value: {value}')

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        print(f'value_to_string: {value}')
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        formfield = super().formfield(**kwargs)
        formfield.coerce = self.get_prep_value
        return formfield
