from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

from .managers import UserManager

# Create your models here.

class User(AbstractUser):
    # additional fields 
    username=None
    email = models.EmailField(_('email address'), unique=True, error_messages={'unique': 'Email address already exists for another user'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # custom user manager
    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"