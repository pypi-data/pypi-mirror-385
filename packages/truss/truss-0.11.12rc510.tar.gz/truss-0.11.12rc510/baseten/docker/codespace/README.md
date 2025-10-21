# Baseten codespace base image

This directory contains the Dockerfile for the Baseten codespace (dev container) base image. It's prebuilt to contain common tools and dependencies, reducing the initial startup time for codespace containers.

## How to build

From this directory:

```sh
# Credentials in 1Password
docker login -u basetenservice
# Check for latest version number on https://hub.docker.com/repository/docker/baseten/baseten-codespace/tags
docker buildx build --platform=linux/amd64 . -t baseten/baseten-codespace:[new version] --push
```

Then update `.devcontainer/Dockerfile` to use the new base image version.
