import pytest
from django.test import Client
from pytest_factoryboy import register

from searcher.tests.factories import ActorFactory, MovieFactory

register(ActorFactory)
register(MovieFactory)


@pytest.fixture(scope="session")
def client():
    return Client()
