from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .values import A, B


from django.forms.fields import TypedChoiceField


# class Fake:
#     def __init__(self, repr):
#         self.repr = repr
#     def __repr__(self):
#         return f'Fake({self.repr})'


# A = Fake('A')
# B = Fake('B')


# class ABField(models.CharField):
#     empty_strings_allowed = False

#     def __init__(self, *args, **kwargs):
#         kwargs['max_length'] = 1
#         super().__init__(*args, **kwargs)
#         self.choices = [('a', _('A')), ('b', _('B'))]
#         self.refs = {A: 'a', B: 'b'}
#         self.derefs = {'a': A, 'b': B}

#     def deconstruct(self):
#         name, path, args, kwargs = super().deconstruct()
#         del kwargs["max_length"]
#         del kwargs["choices"]
#         return name, path, args, kwargs

#     def from_db_value(self, value, expression, connection):
#         return self.to_python(value)

#     def to_python(self, value):
#         if isinstance(value, str):
#             return self.derefs[value]
#         return value

#     def get_prep_value(self, value):
#         if isinstance(value, str):
#             return value
#         if value in self.refs:
#             return self.refs[value]
#         raise Exception(f'Invalid value: {value!r}')

#     def value_to_string(self, obj):
#         value = self.value_from_object(obj)
#         return self.get_prep_value(value)

#     def clean(self, value, model_instance):
#         # Use the str value rather than the class for validation.
#         value = self.get_prep_value(value)
#         self.validate(value, model_instance)
#         self.run_validators(value)
#         return value

#     def formfield(self, **kwargs):
#         formfield = super().formfield(**kwargs)
#         formfield.coerce = self.get_prep_value
#         return formfield


# class ABField(models.CharField):
#     """Provides a hook field based on a CharField."""

#     def __init__(self, *args, max_length=32, **kwargs):

#         super().__init__(*args, max_length=max_length, **kwargs)

#         self.choices = [('a', _('A')), ('b', _('B'))]
#         self.refs = refs = {A: 'a', B: 'b'}
#         self.derefs = {'a': A, 'b': B}
#         self.hook = self.derefs

#         # Create a local class to override the coerce function to
#         # get the key field's value.
#         class HookChoiceField(TypedChoiceField):
#             def __init__(self, *args, **kwargs):
#                 super().__init__(*args, **kwargs)

#                 def hook_coerce(val):
#                     return val if isinstance(val, str) else refs.get(val)
#                 self.coerce = hook_coerce

#         self.hook_choice_field_class = HookChoiceField

#     @property
#     def choices(self):
#         """Dynamically get the choices from the hook."""
#         return [(key, key) for key in sorted(self.hook.keys())]

#     @choices.setter
#     def choices(self, value):
#         """Ignore values set to choices by superclass.
#         The superclass init sets the choices explicitly, but we need
#         to override that dynamically. To do that, we can just avoid
#         having it error by making the setter a black hole.
#         """

#     def to_python(self, value):
#         if isinstance(value, str):
#             return self.hook[value]
#         return value

#     def clean(self, value, model_instance):
#         """
#         Convert the value's type and run validation. Validation errors
#         from to_python() and validate() are propagated. Return the correct
#         value if no error is raised.
#         """
#         # Use the str value rather than the class for validation.
#         value = self.get_prep_value(value)
#         self.validate(value, model_instance)
#         self.run_validators(value)
#         return value

#     def formfield(self, **kwargs):
#         return super().formfield(
#             choices_form_class=self.hook_choice_field_class, **kwargs
#         )

#     def get_prep_value(self, value):
#         if isinstance(value, str):
#             return value
#         if value in self.refs:
#             return self.refs.get(value)
#         raise Exception(f'Invalid value: {value!r}')

#     def from_db_value(self, value, expression, connection):
#         return self.to_python(value)

#     def value_to_string(self, obj):
#         value = self.value_from_object(obj)
#         return self.get_prep_value(value)

#     def deconstruct(self):
#         """Deconstruct this field for generating migrations."""
#         name, path, args, kwargs = super().deconstruct()
#         kwargs["choices"] = []
#         return name, path, args, kwargs


from django.forms import TypedChoiceField
from django.db.models import CharField


class HookField(CharField):
    """Provides a hook field based on a CharField."""

    def __init__(self, *args, hook=None, key_field="key", max_length=32, **kwargs):
        self.hook = {} if hook is None else hook
        self.key_field = key_field

        super().__init__(*args, max_length=max_length, **kwargs)

        # Create a local class to override the coerce function to
        # get the key field's value.
        class HookChoiceField(TypedChoiceField):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                def hook_coerce(val):
                    return (
                        val if isinstance(val, str) else getattr(val, key_field, None)
                    )

                self.coerce = hook_coerce

        self.hook_choice_field_class = HookChoiceField

    @property
    def choices(self):
        """Dynamically get the choices from the hook."""
        return [(key, key) for key in sorted(self.hook.keys())]

    @choices.setter
    def choices(self, value):
        """Ignore values set to choices by superclass.

        The superclass init sets the choices explicitly, but we need
        to override that dynamically. To do that, we can just avoid
        having it error by making the setter a black hole.
        """

    def to_python(self, value):
        if isinstance(value, str):
            return self.hook[value]
        return value

    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors
        from to_python() and validate() are propagated. Return the correct
        value if no error is raised.
        """
        # Use the str value rather than the class for validation.
        value = self.get_prep_value(value)
        self.validate(value, model_instance)
        self.run_validators(value)
        return value

    def formfield(self, **kwargs):
        return super().formfield(
            choices_form_class=self.hook_choice_field_class, **kwargs
        )

    def get_prep_value(self, value):
        if not isinstance(value, str):
            value = getattr(value, self.key_field, None)
        return value

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def deconstruct(self):
        """Deconstruct this field for generating migrations."""
        name, path, args, kwargs = super().deconstruct()
        kwargs["choices"] = []
        return name, path, args, kwargs
