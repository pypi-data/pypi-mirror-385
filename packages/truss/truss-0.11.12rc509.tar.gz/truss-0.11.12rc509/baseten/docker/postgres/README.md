# Baseten Postgres base image

We rely on a [wal2json](https://github.com/eulerto/wal2json) extension for Postgres, but no official repository publishes both amd64 and arm64 images. Therefore, we maintain our own image, which is
heavily based off [bitnami](https://github.com/betaboon/bitnami-postgresql-wal2json/blob/main/Dockerfile)

This is purely used in codespaces / local development environments.

## How to build

From this directory:

```sh
# Credentials in 1Password
docker login -u basetenservice
# Check for latest version number on https://hub.docker.com/repository/docker/baseten/postgres-wal2json/tags
docker buildx build --platform linux/amd64,linux/arm64 . -t baseten/postgres-wal2json:[new version] --push
```

Then update `.devcontainer/Dockerfile` to use the new base image version.
