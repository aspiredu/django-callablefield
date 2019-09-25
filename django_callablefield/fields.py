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


class ABField(models.CharField):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        super().__init__(*args, **kwargs)
        self.choices = [('a', _('A')), ('b', _('B'))]
        self.refs = {A: 'a', B: 'b'}
        self.derefs = {'a': A, 'b': B}

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["choices"]
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value in self.derefs:
            return self.derefs[value]
        raise ValidationError('Invalid value for parsing.')

    def get_prep_value(self, value):
        if isinstance(value, str):
            return value
        if value in self.refs:
            return self.refs[value]
        raise Exception(f'Invalid value: {value!r}')

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def clean(self, value, model_instance):
        # Use the str value rather than the class for validation.
        value = self.get_prep_value(value)
        self.validate(value, model_instance)
        self.run_validators(value)
        return value

    def formfield(self, **kwargs):
        formfield = super().formfield(**kwargs)
        formfield.coerce = self.get_prep_value
        return formfield
