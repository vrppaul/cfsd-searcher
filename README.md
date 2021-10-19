# CSFD movies parser

> ⚠️ **DISCLAIMER**: This project is `development only` version,
> it won't be deployed to any production environment.
> Thus, any sensitive data may freely live in the repo.

Simple web application, which can show actors and movie names from the list of
300 best movies from https://www.csfd.cz/zebricky/filmy/nejlepsi/ website.


## How to launch locally

### Docker start

- Easiest way if you have `docker` and `docker-compose` installed is to run `make` command,
which will run the docker container at the background:
```shell
make start
```
Server will be available at http://0.0.0.0:8000/

- Similarly, server can be stopped with another `make` command:
```shell
make stop
```

### Local python start

- Install `Python3.9`, if you don't have it
- Create a virtual env
- Install dependencies
- Launch the server via `python manage.py runserver`



## How to develop

### Required tools

- Python3.9

### Optional tools

- docker and docker-compose
- pre-commit
- make

### Testing

Run tests from the root folder with `pytest --cov` command.
