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
    slug = models.SlugField(db_index=True)
    actors = models.ManyToManyField("Actor", related_name="movies")

    class Meta:
        ordering = ("slug",)


class Actor(models.Model):
    """
    Represents a single actor entity.
    Has an m2m connection with Movie model.
    """

    name = models.CharField(max_length=ACTOR_NAME_MAX_LENGTH, unique=True)
    slug = models.SlugField(unique=True, db_index=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("slug",)


@receiver(post_save, sender=Movie)
def update_slug_on_creation(instance: Movie, created: bool, **kwargs):
    """
    If new movie instance is created, change its slug to id-slugged-name string.
    Performed as a signal, since movies can have similar names,
    and we need to be able use id as part of a slug.
    """
    if created:
        instance.slug = slugify(f"{instance.pk}-{instance.name}")
        instance.save(update_fields=("slug",))
