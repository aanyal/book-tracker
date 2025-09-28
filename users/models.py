from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from books.models import Book, Genres
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def _create_user(self, username, password):
        user = self.model(
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, password, email=None):
        user = self._create_user(username, password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, username, password, email=None):
        user=self._create_user(username, password)

        return user

class CustomUser(AbstractUser):
    email = models.EmailField(blank=True, null=True)

    objects = CustomUserManager()

    # REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
class CustomUserProfile(models.Model):
    genres = models.ManyToManyField(Genres, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        print(self.genres)
        return ""