from django.db import models
from .fields import ABField

class ABModel(models.Model):
    ab = ABField()
