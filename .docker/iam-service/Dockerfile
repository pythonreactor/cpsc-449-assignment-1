FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt update && \
    apt install -y git curl gnupg lsb-release \
    build-essential libjpeg-dev libpng-dev libtiff-dev \
    socat

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
COPY iam_service/fim-*.tar.gz /code/
COPY iam_service/pyproject.toml /code/pyproject.toml
COPY iam_service/poetry.toml /code/poetry.toml
COPY iam_service/poetry.lock /code/poetry.lock

# Install dependencies
RUN apt-get clean && \
    pip install --upgrade pip && \
    pip install ipython && \
    pip install poetry

# Install the ENV requirements
RUN poetry config virtualenvs.create false

# Setup iPython configuration
RUN ipython profile create
RUN echo "c.InteractiveShellApp.exec_files = ['/code/ipython_setup.py']" >> /root/.ipython/profile_default/ipython_config.py

WORKDIR /code/src/iam

RUN mkdir /docker-build-tools
COPY .docker/entrypoint.sh /docker-build-tools/entrypoint.sh
COPY .docker/await-db.sh /docker-build-tools/await-db.sh

# Clean up stagnant files/data
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/docker-build-tools/entrypoint.sh"]
