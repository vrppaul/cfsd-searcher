from django.urls import path

from . import views

urlpatterns = [
    path("", views.SearchView.as_view(), name="search"),
    path("actors/<slug:slug>/", views.ActorView.as_view(), name="actor-detail"),
    path("movies/<slug:slug>/", views.MovieView.as_view(), name="movie-detail"),
]
