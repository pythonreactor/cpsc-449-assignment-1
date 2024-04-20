FROM python:3.11-slim-bookworm

ENV PORT 5000
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt update && \
    apt install -y git curl wget gnupg lsb-release \
    build-essential libjpeg-dev libpng-dev libtiff-dev \
    socat

# Install and configure zsh
RUN apt-get update && \
    apt-get install -y zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
COPY ./.docker/.zshrc /root/.zshrc

# Install MongoDB packages
RUN curl -fsSL https://pgp.mongodb.com/server-7.0.asc | gpg  --dearmor -o /etc/apt/trusted.gpg.d/mongodb-server-7.0.gpg && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
RUN apt update && \
    apt install -y mongodb-org

# Make the Flask log directory
RUN mkdir -p /var/log/fim-logs

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

# Setup iPython configuration
RUN ipython profile create
RUN echo "c.InteractiveShellApp.exec_files = ['/code/ipython_setup.py']" >> /root/.ipython/profile_default/ipython_config.py

# Set zsh as the default shell
SHELL ["/bin/zsh", "-c"]

WORKDIR /code/src/flask_app

RUN mkdir /docker-build-tools
COPY .docker/entrypoint.sh /docker-build-tools/entrypoint.sh
COPY .docker/await-db.sh /docker-build-tools/await-db.sh

# Clean up stagnant files/data
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/docker-build-tools/entrypoint.sh"]
