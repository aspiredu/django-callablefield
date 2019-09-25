from django.db import models
from .fields import HookField


class Fake:
    def __init__(self, repr, key):
        self.repr = repr
        self.key = key
    def __repr__(self):
        return f'Fake({self.repr})'


A = Fake('A', 'a')
B = Fake('B', 'b')


abhook = {'a': A, 'b': B}


class ABModel(models.Model):
    ab = HookField(hook=abhook, key_field='key')

    def __str__(self):
        return f'ABModel(ab={self.ab!r})'
