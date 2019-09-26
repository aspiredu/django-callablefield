from django.db import models
from django.utils.translation import gettext_lazy as _
from .hook import HookField
from .myhook import myhook


class ABModel(models.Model):
    ab_key, ab = HookField.with_property(hook=myhook, max_length=32)

    def __str__(self):
        return f'ABModel(ab={self.ab!r})'



class Fake:
    def __init__(self, repr):
        self.repr = repr
    def __repr__(self):
        return f'Fake({self.repr!r})'


A = Fake('A')
B = Fake('B')


# Register hook values after the model is created
# to maximally mess with the choices stuff.
myhook.register('a', A, label=_('AA'))
myhook.register('b', B, label=_('BB'))
