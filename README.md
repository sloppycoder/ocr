
# Welcome to your Python project

This project is set up Python project with dev tooling pre-configured

* black
* flake8
* isort
* mypy
* VS Code support

## Setup

The easiest way to get started is use [Visual Studio Code with devcontainer](https://code.visualstudio.com/docs/devcontainers/containers)

The more traditional way is to install python 3.11 and [poetry](https://python-poetry.org/), then


```shell

# create virtualenv
poetry shell

# install dependencies
poetry install --no-root --with linting
```

## Develop the code for the stack

```shell

# update your DATABASE_URL is used
# create database and assign proper privileges to the user
# e.g.
# create database mydb;
# grant all privileges on database mydb to me;

nano .env

# run alembic migration
alembic upgrade head

# run unit tests
pytest

```

## generate code using config file without interactive input

Create a [config file](sample_prog.json) with options to use, then

```shell

cookiecutter gh:vino9org/cookiecutter-python --config-file sample_prog.json --no-input

```
