from django.db import models

# Create your models here.

class Foo(models.Model):
    name = models.CharField(max_length=255)
