# Encrypted Textsearch Poc

# Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.


# Run the service

* Install project dependencies
```shell
$ poetry install
```

* Start the service with Docker Compose:
```shell
$ docker-compose up -d
```

* Or run it with poetry
```shell
$ poetry run main.py
```

# Start
Open your browser at http://0.0.0.0:8000/docs, and you'll see the swagger interface 
which will allow you to add new messages (with application-side encryption) and to 
search through this messages 
