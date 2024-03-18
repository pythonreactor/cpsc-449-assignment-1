# The python image from Docker we want to use as a base
FROM python:3.11-slim-bookworm

ENV PORT 8000
ENV PYTHONUNBUFFERED 1

# Install and configure zsh
RUN apt-get update && \
    apt-get install -y git zsh curl
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
COPY ./.docker/.zshrc /root/.zshrc

# Make the Django log directory
RUN mkdir -p /var/log/cpsc-449-1-logs

RUN mkdir -p /code
WORKDIR /code

# Copy the requirements files
# We're using a docker-compose volume so we don't copy the source code initially
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.toml /code/poetry.toml
COPY ./poetry.lock /code/poetry.lock

# Install dependencies
RUN apt-get clean && \
    pip install --upgrade pip && \
    pip install ipython && \
    pip install poetry

# Install the ENV requirements
RUN poetry install

# Set zsh as the default shell
SHELL ["/bin/zsh", "-c"]

# WORKDIR /code

WORKDIR /code/src/flask_app
