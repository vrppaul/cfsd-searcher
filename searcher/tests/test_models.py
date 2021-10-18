from typing import Type

from django.utils.text import slugify
import pytest

from .factories import ActorFactory, MovieFactory


@pytest.mark.django_db
def test_correct_actor_slug(actor_factory: Type[ActorFactory]):
    actor = actor_factory()
    assert actor.slug == slugify(actor.name)


@pytest.mark.django_db
def test_correct_movie_slug(movie_factory: Type[MovieFactory]):
    movie = movie_factory()
    assert movie.slug == slugify(f"{movie.id} {movie.name}")


@pytest.mark.django_db
def test_movies_same_name_different_slug(movie_factory: Type[MovieFactory]):
    first, second = movie_factory.create_batch(2, name="same")
    assert first.slug != second.slug
