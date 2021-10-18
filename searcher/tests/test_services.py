from typing import Type, Union, Callable

import faker
import pytest
from django.http import Http404

from .factories import ActorFactory, MovieFactory
from searcher import models, services


fake = faker.Faker()


@pytest.mark.django_db
def test_is_db_empty_empty():
    assert services.is_db_empty()


@pytest.mark.django_db
def test_is_db_empty_not_empty(
        actor_factory: Type[ActorFactory],
        movie_factory: Type[MovieFactory]
):
    # Test if some actors and movies exist
    actor_factory.create_batch(3)
    movie_factory.create_batch(3)
    assert not services.is_db_empty()

    # Test if only actors exist
    models.Movie.objects.all().delete()
    assert not services.is_db_empty()
    models.Actor.objects.all().delete()

    # Test if only movies exist
    actor_factory.create_batch(3)
    assert not services.is_db_empty()


@pytest.mark.django_db
def test_clean_db(
        actor_factory: Type[ActorFactory],
        movie_factory: Type[MovieFactory]
):
    actor_factory.create_batch(3)
    movie_factory.create_batch(3)
    services.clean_db()
    assert not models.Actor.objects.exists()
    assert not models.Movie.objects.exists()


@pytest.mark.django_db
def test_create_movie_with_actors_single_movie():
    services.create_movie_with_actors(fake.name(), [fake.name() for _ in range(10)])

    # Test single movie was created with correct data
    assert models.Movie.objects.count() == 1
    movie = models.Movie.objects.first()
    assert movie.name and movie.slug

    # Test multiple actors were created with corresponding movie
    assert models.Actor.objects.count() == 10
    for actor in models.Actor.objects.all():
        assert actor.name and actor.slug
        assert movie in actor.movies.all()


@pytest.mark.django_db
def test_actors_wont_be_recreated():
    common_actors = [f"{i} actor" for i in range(5)]

    services.create_movie_with_actors(
        fake.name(),
        [f"{i} actor" for i in range(5, 10)] + common_actors
    )
    services.create_movie_with_actors(
        fake.name(),
        [f"{i} actor" for i in range(10, 15)] + common_actors
    )

    assert models.Movie.objects.count() == 2
    assert models.Actor.objects.count() == 15
    for movie in models.Movie.objects.all():
        assert movie.actors.count() == 10


@pytest.mark.django_db
def test_get_movies_and_actors_by_query_both_exist(
        actor_factory: Type[ActorFactory],
        movie_factory: Type[MovieFactory]
):
    specific_name = "Very Specific and Unique Name"
    specific_actor = actor_factory(name=specific_name)
    actor_factory.create_batch(10)
    specific_movie = movie_factory(name=specific_name)
    movie_factory.create_batch(10)

    movies, actors = services.get_movies_and_actors_by_query("y specific a")
    assert movies.count() == 1
    assert specific_movie in movies
    assert actors.count() == 1
    assert specific_actor in actors


@pytest.mark.django_db
def test_get_movies_and_actors_by_query_actor_exist(
        actor_factory: Type[ActorFactory],
        movie_factory: Type[MovieFactory]
):
    specific_name = "Very Specific and Unique Name"
    actor_factory(name=specific_name)
    actor_factory.create_batch(10)
    movie_factory.create_batch(10)

    movies, actors = services.get_movies_and_actors_by_query("y specific a")
    assert not movies.exists()
    assert actors.exists()


@pytest.mark.django_db
def test_get_movies_and_actors_by_query_movie_exist(
        actor_factory: Type[ActorFactory],
        movie_factory: Type[MovieFactory]
):
    specific_name = "Very Specific and Unique Name"
    actor_factory.create_batch(10)
    movie_factory(name=specific_name)
    movie_factory.create_batch(10)

    movies, actors = services.get_movies_and_actors_by_query("y specific a")
    assert movies.exists()
    assert not actors.exists()


@pytest.mark.django_db
def test_get_movies_and_actors_by_query_movie_exist(
        actor_factory: Type[ActorFactory],
        movie_factory: Type[MovieFactory]
):
    actor_factory.create_batch(10)
    movie_factory.create_batch(10)

    movies, actors = services.get_movies_and_actors_by_query("y specific a")
    assert not movies.exists()
    assert not actors.exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory, get_by_slug_method", [
        (ActorFactory, services.get_actor_by_slug),
        (MovieFactory, services.get_movie_by_slug)
    ]
)
def test_get_model_by_slug(
        factory: Type[Union[ActorFactory, MovieFactory]],
        get_by_slug_method: Callable
):
    actor, *_ = factory.create_batch(10)
    found_actor = get_by_slug_method(actor.slug)
    assert actor == found_actor

    with pytest.raises(Http404):
        get_by_slug_method("random-not-existing-slug")
