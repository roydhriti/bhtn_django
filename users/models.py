from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255 , unique=True)
    password = models.CharField(max_length=255)
    username = None # using custome email password...

    USERNAME_FIELD = 'email' # mandatory for overwrite django username
    REQUIRED_FIELDS = []