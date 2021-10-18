import factory


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "searcher.Movie"

    name = factory.Faker("sentence")


class ActorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "searcher.Actor"

    name = factory.Faker("name")
