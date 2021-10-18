import logging
from functools import partial
from multiprocessing.pool import ThreadPool
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser
import requests
from tenacity import Retrying, stop_after_attempt, wait_exponential

from searcher import services


REQUEST_HEADERS = {"User-Agent": settings.PARSER_USER_AGENT}
RETRY_ATTEMPTS = 2

lxml_soup = partial(BeautifulSoup, features="lxml")

logger = logging.getLogger("parser")


class Command(BaseCommand):
    """
    Parses TOP 300 movies from CSFD website and saves them and their actors to the DB.
    """

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--num-threads", "-n", type=int, default=10,
            help="Num of threads to simultaneously process movies parsing"
        )

    def handle(self, *args, **options):
        if not services.is_db_empty():
            handle_db_rewrite()
        logger.info("Starting parsing CSFD movies.")
        parse_movies_and_actors_to_db(settings.PARSER_BASE_URL, options["num_threads"])


def handle_db_rewrite() -> None:
    rewrite_db = input("DB is not empty, do you want to rewrite data? [yN]: ").lower() or "n"
    if rewrite_db == "y":
        logger.info("Deleting existing DB data.")
        services.clean_db()
    elif rewrite_db == "n":
        logger.info("Parsing aborted.")
        exit(0)
    else:
        raise CommandError("Unknown command for data rewrite.")


def parse_movies_and_actors_to_db(base_url: str, num_threads: int = 10) -> None:
    """
    Parses movies from CSFD website and saves them to the DB.
    Work is paralleled into several threads.
    @param base_url: str, base url of CSFD website.
    @param num_threads: int, num of threads to run in parallel.
    """
    movie_urls = parse_movie_urls(urljoin(base_url, "/zebricky/filmy/nejlepsi/?showMore=1"))
    parse_movies_and_actors_with_base = partial(parse_movies_with_actors, base_url=base_url)
    with ThreadPool(num_threads) as pool:
        movies_with_actors = pool.map(parse_movies_and_actors_with_base, movie_urls)
    for movie_name, actor_names in movies_with_actors:
        services.create_movie_with_actors(movie_name, actor_names)


def parse_movie_urls(list_url: str) -> tuple[str, ...]:
    """
    Parses the list of movie urls from a provided url.
    @param list_url: str, url, where movies list lives.
    @return: tuple of movie urls.
    """
    logger.debug("Parsing movies list")
    try:
        for attempt in Retrying(
                stop=stop_after_attempt(RETRY_ATTEMPTS),
                wait=wait_exponential(multiplier=1),
                reraise=True
        ):
            with attempt:
                r = requests.get(list_url, headers=REQUEST_HEADERS)
                r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise CommandError(f"Couldn't parse the list o movies. Reason: {e}")

    try:
        soup = lxml_soup(r.text)
        return tuple(
            element.attrs["href"] for element
            in soup.find_all("a", class_="film-title-name")
        )
    except KeyError:
        raise CommandError(
            "Some parsed movies do not have a href attribute. "
            "Is search by attribute correct?"
        )


def parse_movies_with_actors(movie_url: str, base_url: str) -> tuple[str, tuple[str, ...]]:
    """
    For a provided movie url, parses its name and actors list.
    @param movie_url: str, relative url of a movie.
    @param base_url: str, base url of CSFD website.
    @return: tuple, first value is movie name, second is tuple of actor names.
    """
    logger.debug("Parsing move with url: %s", movie_url)

    try:
        for attempt in Retrying(
                stop=stop_after_attempt(RETRY_ATTEMPTS),
                wait=wait_exponential(multiplier=1),
                reraise=True
        ):
            with attempt:
                r = requests.get(urljoin(base_url, movie_url), headers=REQUEST_HEADERS)
                r.raise_for_status()
    except requests.exceptions.RequestException:
        logger.exception("Couldn't parse a movie with url %s after all attempts", movie_url)
        return tuple()

    try:
        return parse_movies_with_actors_from_html(r.text)
    except AttributeError:
        logger.exception("Movie info parsing failed, some crucial element was not found")
        return tuple()


def parse_movies_with_actors_from_html(html_content: str) -> tuple[str, tuple[str, ...]]:
    """
    From a provided html content parses movie name and actors names.
    @param html_content: str, content of a url, where movie info lives.
    @return: tuple, first value is movie name, second is tuple of actor names.
    """
    soup = lxml_soup(html_content)
    movie_name = soup.find("div", class_="film-header-name").h1.text.strip()
    movie_actors_element = soup.find("h4", string="Hrají: ").parent.find("span")
    all_actors = tuple(
        actor.get_text() for actor
        in movie_actors_element.find_all("a", class_=lambda s: s != "more")
    )
    return movie_name, all_actors


