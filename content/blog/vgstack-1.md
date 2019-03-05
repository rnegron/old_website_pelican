title: Full-Stack Project: vg-stack (Part 1)
date: 2019-01-19
slug: vgstack-1
category: blog
tags: web, programming, python, django, docker, vgstack

# Motivation

In the web development space, tools and best-practices change quite frequently. At one point in the not-so-distant past, a [LAMP](https://en.wikipedia.org/wiki/LAMP_%28software_bundle%29) stack was the go-to approach for launching a web application. These days, PHP is the #8 most popular programming language (according to a company with the name ["The Importance Of Being Earnest"](https://www.tiobe.com/tiobe-index/)), while Python and JavaScript rank above it.

One of the reason for this change has to do with the growing trend towards microservice architectures. Together with the need for rapid prototyping and the onset of agile development methodologies, Python and other languages have swept in and stolen the LAMP stack's lunch.

So what is the _new stack_? A complex question with opinionated answers... Here is a recent community discussion on Hacker News: [Go-to web stack today?](https://news.ycombinator.com/item?id=18829557)

But wow, there are so many things to learn and keep up to date with nowadays! To help alleviate this, I'd like to work on a side-project using full-stack technologies. In particular, I want to use the following tools to build a fullstack app:

- Django (backend)
- Angular (frontend)
- Docker (development/deployment)
- Postgres (database)
- ... plus many more! (think git, pipenv, serverless, test-driven development... Maybe type-hints, GraphQL and data visualization too?)

# The idea: A web app for keeping track of your video game backlog

No shame: the project is most definitely a copy of [The Backloggery](https://backloggery.com), a great site that I use often. However, as far as I know, The Backloggery is [built in PHP](https://backloggery.com/about.php), probably on a LAMP stack or similar. So I thought I would take a crack at building a small subset of the Backloggery features, on a more modern stack.

I like this idea because it comes with a well-defined problem set. I can already envision the database schema and how to build the backend. But as I mentioned, this project is going to involve the entire stack. That means I gotta learn some frontend JavaScript. In this series of blog posts, I document my experience.

> I should say, the reason I picked [Angular](https://angular.io/) and not (the elephant in the room) [React](https://reactjs.org/) is that in my [day job](https://www.abartyshealth.com), our frontend team works with Angular and so this is a skill I would like to improve! Besides, we all know [Postgres](https://en.wikipedia.org/wiki/PostgreSQL) is the real elephant here, right? Let's move on.

# The app: vg-stack

I had to name my repo something!

In all honestly, I like the name because it hints at the purpose of the project (practicing the web stack) while at the same conjuring a mental image of a bunch of video games stacked on top of each other.

## Setting up

For this first part, I'm going to build a backend skeleton using Django and the awesome [Django REST framework](https://www.django-rest-framework.org/) package. As already mentioned, our database will be the ever-popular PostgreSQL and we are aiming for best practices in all parts of the stack. That includes deployment/development tools and environments! That said, I'm going to assume knowledge of the tools used and explain only the highlights.

## Project Structure

In fact, I'm going to skip most of the project setup entirely and just go with a pre-built template! I like William Vincent's [drfx](https://github.com/wsvincent/drfx), so let's go ahead and clone that:

```shell
$ git clone https://github.com/wsvincent/drfx vgstack
```

The template provided comes with a lot of best practices built in. We can build on top of it and get going quickly!

### Dependencies

We're going to install the following extra packages for now:
[python-dotenv](https://github.com/theskumar/python-dotenv) to comply with [mandate III](https://12factor.net/config) of The Twelve-Factor App, [psycopg2-binary](https://github.com/psycopg/psycopg2) to use PostgreSQL as our database, [black](https://github.com/ambv/black) to format our code and [factory_boy](https://github.com/FactoryBoy/factory_boy) to improve our tests maintenance.

```shell
$ pipenv install python-dotenv psycopg2-binary
```

```shell
$ pipenv install --pre --dev black factory_boy
```

We install `black` and `factory_boy` as development dependencies and tell Pipenv to allow the pre-release `black` package through!

## Django Settings

Let's get started setting up our project.

First, create a `.env` file for use with `python-dotenv`.

```env
# vgstack/.env

DEBUG=on
SECRET_KEY=your-secret-key
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=postgres
DATABASE_HOST=database
DATABASE_PORT=5432
```

Replace the `SECRET_KEY` with an actual secret key! You can generate one in Python:

```python
from django.core.management.utils import get_random_secret_key

get_random_secret_key()
```

The database env variables can stay as they are, since those settings happily coincide with the default database, user and password in the [Postgres Docker Image](https://hub.docker.com/_/postgres)!

Now, replace "drfx" with "vgstack" everywhere it appears in the project, such as in values for `ROOT_URLCONF`, `WSGI_APPLICATION` and even the main "drfx" directory!

We also modify our settings file in order to use `python-dotenv`. In the end, it should look like this:

```python
# vgstack/vgstack/settings.py

from pathlib import Path
import os
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=dotenv_path)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# Allow communicaiton from our Docker container if DEBUG=True
ALLOWED_HOSTS = ["0.0.0.0"] if DEBUG else []

# ...

ROOT_URLCONF = "vgstack.urls"

# ...

WSGI_APPLICATION = "vgstack.wsgi.application"

# Database
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv("DATABASE_NAME"),
    "USER": os.getenv("DATABASE_USER"),
    "PASSWORD": os.getenv("DATABASE_PASSWORD"),
    "HOST": os.getenv("DATABASE_HOST"),
    "PORT": os.getenv("DATABASE_PORT"),
    "CONN_MAX_AGE": 7200,
  }
}

# ...
```

Notice I replaced the `os.path` call for the new kid on the block: `Pathlib`. I'm trying to make that a habit!

### Docker

Let's build a simple Python Dockerfile!

```docker
# vgstack/Dockerfile

# pull the Python official base image, slimmed down
FROM python:3.7-slim

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/app

# install dependencies with Pipenv
RUN pip install --upgrade pip && pip install pipenv
COPY ./Pipfile /usr/src/app/Pipfile
RUN pipenv install --system --skip-lock

# copy project over to image
COPY . /usr/src/app/

# specify our entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]
```

And a nice docker-compose file to help us run the project and related services.

```docker
# vgstack/docker-compose.yml

version: '3.7'

services:
  database:
    image: postgres:11-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/

  web:
    build: .
    entrypoint: /usr/src/app/docker-entrypoint.sh
    volumes:
      - ./:/usr/src/app/
    ports:
      - 8000:8000
    env_file: .env
    depends_on:
      - database
volumes:
  postgres_data:
    external: false
```

We can see that we are persisting the Postgres database via Docker volumes. Also, we are taking advantage of the `env_file` command to load in our previously created file. Finally, we call the `entrypoint` command to run a shell script instead of running an in-line command.

The following entrypoint script is a modified version of the one found in José Padilla's [notaso](https://github.com/jpadilla/notaso) project. It attempts to use a PostgreSQL cursor every second, and keeps trying until a connection succeeds. Then, it proceeds to migrate the Django models and runs the development server.

```shell
#!/bin/sh

# vgstack/docker-entrypoint.sh

set -e

postgres_ready(){
python manage.py shell << END
import sys
import psycopg2
from django.db import connections
try:
    connections['default'].cursor()
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
    >&2 echo "==> Waiting for Postgres..."
    sleep 1
done

echo "==> Postgres started!"

python manage.py makemigrations users
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

exec "$@"
```

**Note**: Make sure to `chmod +x docker-entrypoint.sh`!

### Sanity check

We can now use docker-compose to build our images and start our development server!

```shell
$ docker-compose up --build
```

Visiting [http://0.0.0.0:8000](http://0.0.0.0:8000) on your browser should show... a 404 page. That's by design! There's no home page yet. Pointing the browser over to [http://0.0.0.0:8000/admin/](http://0.0.0.0:8000/admin/) should show a log in screen, which means all is well! You can create a user by opening a new terminal window and using Python inside the running Docker container. 

```shell
$ docker-compose exec web python manage.py createsuperuser
```

You may want to start the containers in detached mode so you don't have to keep opening terminal windows.

```shell
$ docker-compose up -d
```

### Applying a `black` coat of paint

After all that, it's nice to make sure our code looks nice and consistent. For that, we can use the opinionated Python code formatter, black.

First, create a `pyproject.toml` file in the root of the project, in order to customize black's settings if we so choose.

```
# vgstack/pyproject.toml

[tool.black]
line-length = 88
```

And now, format:

```shell
$ black .
```

Looking good.

## Up Next

Now that the project is set up with best practices thanks to `drfx` and we have a nice development workflow using Docker, we can get to work writing the actual bulk of the backend. In the next part, we will write the models, serializers, views and (last but not least) the tests that make up our backend code.

# Resources:

- <https://wsvincent.com/django-docker-postgresql/>
- <https://docs.djangoproject.com/en/2.1/ref/settings/>
