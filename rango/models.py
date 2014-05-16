import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.CharField(max_length=128, unique=True, editable=False,
                            blank=True)

    def save(self, **kwargs):
        slug = re.sub(r'[^a-zA-Z0-9/_|+ -]', '', self.name)
        slug = re.sub(r'[/_|+ -]+', '-', slug).lower()
        self.slug = slug
        super(Category, self).save()

    def __unicode__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField(unique=True)
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title


class User(AbstractUser):
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='user', blank=True)
