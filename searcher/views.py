from urllib.parse import urlencode

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, FormView

from . import forms, services
from .models import Actor, Movie


class SearchView(FormView):
    """
    Main page, has an input only, if no search query was provided.
    Lists corresponding movies and actors otherwise.
    """

    form_class = forms.SearchForm
    template_name = "search.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        query = self.request.GET.get("q")
        movies, actors = services.get_movies_and_actors_by_query(query)

        return self.render_to_response(
            {
                "form": self.form_class(),
                "query": query,
                "movies": movies,
                "actors": actors,
            }
        )

    def form_valid(self, form: forms.SearchForm) -> HttpResponse:
        query = form.data["search_input"]
        return redirect("/?" + urlencode({"q": query}))


class ActorView(DetailView):
    """
    Single actor info. Shows actor info + movies.
    Correct actor is requested by provided slug.
    """

    template_name = "actor.html"
    model = Actor


class MovieView(DetailView):
    """
    Single movie info. Shows movie info + starring actors.
    Correct movie is requested by provided slug.
    """

    template_name = "movie.html"
    model = Movie
