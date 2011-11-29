from django.db import models

class Email(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now = True)
    invited = models.BooleanField(default = False)

