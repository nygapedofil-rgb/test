from django.db import models

# Create your models here.

class PublicKey(models.Model):
    id = models.IntegerField(primary_key=True)
    key = models.TextField()