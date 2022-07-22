from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="owner", primary_key=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="owner")
    public = models.TextField(verbose_name="public_key")
    private = models.TextField(verbose_name="private_key")


class UserPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="owner")
    login = models.CharField(max_length=255, verbose_name="login")
    password = models.TextField(verbose_name="password")
