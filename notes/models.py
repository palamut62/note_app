from django.utils import timezone  # Bu satırı ekleyin
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Tag(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,  # Geçici olarak null'a izin veriyoruz
        default=settings.AUTH_USER_MODEL  # Varsayılan bir kullanıcı belirliyoruz
    )

    def __str__(self):
        return self.name

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    color = models.CharField(max_length=20, default='yellow')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    reminder = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # created_at alanı eklendi

    def __str__(self):
        return self.user.username
