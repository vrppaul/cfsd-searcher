from typing import Iterable, Optional, Type, TypeVar
from urllib.parse import unquote_plus

from django.db import transaction
from django.db.models import Model, ObjectDoesNotExist, QuerySet
from django.http import Http404
from django.utils.text import slugify

from .models import Actor, Movie


def is_db_empty() -> bool:
    """
    Checks whether actors or movies exist (which are main contents of a db).
    """
    return not Actor.objects.exists() and not Movie.objects.exists()


def clean_db() -> None:
    """
    Cleans actor and movie tables.
    """
    Actor.objects.all().delete()
    Movie.objects.all().delete()


@transaction.atomic
def create_movie_with_actors(movie_name: str, actor_names: Iterable[str]) -> None:
    """
    Creates a movie with provided name.
    Creates or fetches (if exist) actors with provided names,
    assigns those actors to the created movie.
    """
    Actor.objects.bulk_create(
        [Actor(name=actor_name, slug=slugify(actor_name)) for actor_name in actor_names],
        ignore_conflicts=True,
    )
    actors = Actor.objects.filter(name__in=actor_names)
    movie = Movie.objects.create(name=movie_name)
    movie.actors.add(*actors)


def get_movies_and_actors_by_query(query: Optional[str]) -> tuple[QuerySet, QuerySet]:
    """
    Searches through movies and actors to find occurrences of those models by provided query.
    @return: tuple, first argument is movies queryset, second - actors queryset.
    """
    if query:
        query = unquote_plus(query)
        movies = Movie.objects.filter(name__icontains=query)
        actors = Actor.objects.filter(name__icontains=query)
    else:
        movies, actors = Movie.objects.none(), Actor.objects.none()
    return movies, actors


TModel = TypeVar("TModel", bound=Model)


def get_entity_by_slug(model: Type[TModel], slug) -> TModel:
    """
    Searches an instance of a provided model by provided slug.
    @param model: Type[TModel], django model in which an instance should be searched.
    @param slug: parameter for searching.
    @return: found instance.
    @raise: Http404, if no instance was found.
    """
    try:
        return model.objects.get(slug=slug)  # type: ignore
    except ObjectDoesNotExist:
        raise Http404(f"No {model.__name__} matches the given slug.")


def get_actor_by_slug(slug: str) -> Actor:
    return get_entity_by_slug(Actor, slug)


def get_movie_by_slug(slug: str) -> Movie:
    return get_entity_by_slug(Movie, slug)
