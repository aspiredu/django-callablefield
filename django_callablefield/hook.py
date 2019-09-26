from django.db import models


class Hook:
    """A dynamic hook with some Django form knowledge."""

    def __init__(self):
        self.__values: Dict[str, Any] = {}
        self.__labels: Dict[str, Any] = {}

    def register(self, key: str, value, *, label=None):
        """Register a new hook value for the given key.

        Optionally include a label to use as the representation in forms.
        """
        self.__values[key] = value
        self.__labels[key] = label or key

    def identify(self, value):
        if value in self.__values.values():
            return next(k for k, v in self.__values.items())
        raise ValueError(f"{value!r} could not be identified")

    def lookup(self, key):
        if key in self.__values:
            return self.__values[key]
        raise ValueError(f'invalid key: {key!r}')

    def choices(self):
        return list(self.__labels.items())


class HookField(models.CharField):
    """Simple hook value serialization and storage in the database."""
    empty_strings_allowed = False

    @classmethod
    def with_property(cls, *args, hook, **kwargs):
        """Construct the field and create a wrapping property."""
        field = cls(*args, hook=hook, **kwargs)

        @property
        def prop(self):
            key = getattr(self, field.name)
            return hook.lookup(key) if key else None

        @prop.setter
        def prop(self, value):
            setattr(self, field.name, hook.identify(value))

        return field, prop

    def __init__(self, *args, hook=None, **kwargs):
        self.hook = hook
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def formfield(self, *args, **kwargs):
        self.choices = self.hook.choices()
        return super().formfield(*args, **kwargs)
