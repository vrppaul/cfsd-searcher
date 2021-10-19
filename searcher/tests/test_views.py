from http import HTTPStatus
from typing import Type

import pytest
from django.test import Client
from django.urls import reverse

from .factories import ActorFactory, MovieFactory


@pytest.mark.django_db
def test_search_view_without_query(client: Client):
    response = client.get(reverse("search"))
    assert response.status_code == HTTPStatus.OK
    assert response.context["query"] is None
    assert not response.context["movies"].exists()
    assert not response.context["actors"].exists()


@pytest.mark.django_db
def test_search_view_with_query(
    client: Client,
    actor_factory: Type[ActorFactory],
    movie_factory: Type[MovieFactory],
):
    first_actor = actor_factory(name="first actor")
    second_actor = actor_factory(name="second actor")
    first_movie = movie_factory(name="first movie")
    second_movie = movie_factory(name="second movie")

    # Check by first word
    response = client.get(reverse("search") + "?q=first")
    assert response.status_code == HTTPStatus.OK
    assert response.context["query"] == "first"
    response_movies = response.context["movies"]
    response_actors = response.context["actors"]
    assert first_movie in response_movies and second_movie not in response_movies
    assert first_actor in response_actors and second_actor not in response_actors

    # Check by first word
    response = client.get(reverse("search") + "?q=second")
    assert response.status_code == HTTPStatus.OK
    response_movies = response.context["movies"]
    response_actors = response.context["actors"]
    assert second_movie in response_movies and first_movie not in response_movies
    assert second_actor in response_actors and first_actor not in response_actors

    # Check by second word
    response = client.get(reverse("search") + "?q=actor")
    assert response.status_code == HTTPStatus.OK
    response_actors = response.context["actors"]
    assert response.context["movies"].count() == 0
    assert response_actors.count() == 2
    assert second_actor in response_actors and first_actor in response_actors

    # Check by second word
    response = client.get(reverse("search") + "?q=movie")
    assert response.status_code == HTTPStatus.OK
    response_movies = response.context["movies"]
    assert response.context["actors"].count() == 0
    assert response_movies.count() == 2
    assert second_movie in response_movies and first_movie in response_movies

    # Check by fully matching word
    response = client.get(reverse("search") + "?q=first+actor")
    assert response.status_code == HTTPStatus.OK
    response_actors = response.context["actors"]
    assert response_actors.count() == 1
    assert first_actor in response_actors

    # Check by not matching word
    response = client.get(reverse("search") + "?q=not+matching")
    assert response.status_code == HTTPStatus.OK
    assert response.context["actors"].count() == 0
    assert response.context["movies"].count() == 0


@pytest.mark.django_db
def test_post_search(client: Client):
    response = client.post(reverse("search"), data={"search_input": "some"})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse("search") + "?q=some"


@pytest.mark.django_db
def test_get_movie_view(
    client: Client,
    actor_factory: Type[ActorFactory],
    movie_factory: Type[MovieFactory],
):
    actors = actor_factory.create_batch(10)
    movie = movie_factory()
    movie.actors.add(*actors)

    # Existing slug
    response = client.get(reverse("movie-detail", args=[movie.slug]))
    assert response.status_code == HTTPStatus.OK
    movie_response = response.context["movie"]
    assert movie_response == movie
    assert movie_response.actors.count() == 10

    # Not existing slug
    response = client.get(reverse("movie-detail", args=["some-random-slug"]))
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_get_actor_view(
    client: Client,
    actor_factory: Type[ActorFactory],
    movie_factory: Type[MovieFactory],
):
    actor = actor_factory()
    movies = movie_factory.create_batch(10)
    for movie in movies:
        movie.actors.add(actor)

    # Existing slug
    response = client.get(reverse("actor-detail", args=[actor.slug]))
    assert response.status_code == HTTPStatus.OK
    actor_response = response.context["actor"]
    assert response.context["actor"] == actor
    assert actor_response.movies.count() == 10

    # Not existing slug
    response = client.get(reverse("actor-detail", args=["some-random-slug"]))
    assert response.status_code == HTTPStatus.NOT_FOUND
