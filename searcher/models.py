from typing import Union

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

MOVIE_NAME_MAX_LENGTH = 1000
ACTOR_NAME_MAX_LENGTH = 1000


class Movie(models.Model):
    """
    Represents a single movie entity.
    name is not unique, since some movies can potentially have same names.
    """

    name = models.CharField(max_length=MOVIE_NAME_MAX_LENGTH)
    slug = models.SlugField(unique=True, db_index=True)
    actors = models.ManyToManyField("Actor", related_name="movies")

    class Meta:
        ordering = ("slug",)


class Actor(models.Model):
    """
    Represents a single actor entity.
    Has an m2m connection with Movie model.
    """

    name = models.CharField(max_length=ACTOR_NAME_MAX_LENGTH)
    slug = models.SlugField(unique=True, db_index=True)
    csfd_id = models.IntegerField()

    class Meta:
        ordering = ("slug",)


@receiver(post_save, sender=Actor)
@receiver(post_save, sender=Movie)
def update_slug_on_creation(instance: Union[Actor, Movie], created: bool, **kwargs):
    """
    If new actor/movie instance is created, change its slug to id-slugged-name string.
    Performed as a signal, since actors/movies can have similar names,
    and we need to be able to use id as part of a slug.
    """
    if created:
        instance.slug = slugify(f"{instance.pk}-{instance.name}")
        instance.save(update_fields=("slug",))
