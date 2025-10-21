# Dockerfile best practices

Most of our services are build into docker containers as defined by Dockerfiles. Here are some best practices for writing secure and fast Dockerfiles.

## 🔒 Security tips

### Use Chainguard Images

Baseten leverages [Chainguard](https://chainguard.dev/) images for improved security. Chainguard images are regularly rebuilt from source with security patches to address all known vulnerabilities (CVEs).

Use the following images based on the language of your project:

- `registry.infra.basetensors.com/chainguard/chainguard/wolfi-base:latest@sha256:d0142a67efcf16310e0d0f5eb75fc25d293fe04616784f6e7bc57a541d63dd9f` for Go run stage
  - [Wolfi](https://edu.chainguard.dev/open-source/wolfi/overview/) is Chainguard's minimal linux distribution built for supply chain security. It includes the `apk` pacakge manager (similar to Alpine) and runs non-root by default.
- `registry.infra.basetensors.com/chainguard/baseten.co/python:X.Y-dev@sha256:...` for Python (build and run)

Make sure to include the sha256 digest of the image in the Dockerfile to make sure builds are reproducible and we can explicitly update the image with patches if needed.

We use the [Basetensors harbor](https://registry.infra.basetensors.com/) as a pull-through cache for available Chainguard images. Access to harbor should be pre-configured in CI/CD and codespaces. For local development, you can configure your docker client to use the harbor registry by running the following command:

```bash
# Get username and password from `Chainguard cache dev docker cred` in 1password
docker login registry.infra.basetensors.com
```

All Baseten engineers should have access to the [Chainguard console](https://console.chainguard.dev/) via Okta SSO to view available images. Let the infrastructure team know if you need access to additional images.

For information on migrating existing images to Chainguard, see the [Chainguard migration guide](https://edu.chainguard.dev/chainguard/migration/).

### Run as non-root

Always design your Dockerfiles to run as a non-root user in the final image. This is a critical security practice that limits the potential impact of container breaches. Use the `USER nonroot` directive after setting up necessary files and permissions. While you may need root access during the build process, it's important to switch to a non-root user before running the application.

The wolfi base image (see Chainguard section above) includes a `nonroot` user by default.

Here's an example of proper user management:

```dockerfile
USER root
# Install packages or perform root operations
USER nonroot
# Run application
```

### Separate build stages

Multi-stage builds are essential for creating secure and efficient Docker images. They allow you to keep build tools and dependencies in a separate build stage, copying only the necessary artifacts to the final stage. This approach significantly reduces the final image size and attack surface.

Example of a multi-stage build:

```dockerfile
FROM golang:1.23-dev AS builder
# Build application

FROM wolfi-base:latest
# Copy only built binary
```

## 🏃 Performance tips

### Install dependencies before copying source

Optimize your Docker builds by carefully ordering your layers. Always install dependencies before copying your source code. This approach takes advantage of Docker's layer caching system, making subsequent builds much faster when only source code changes. Start by copying dependency files like requirements.txt or go.mod, then install dependencies, and finally copy the source code.

See the [operator Dockerfile](../../operator/Dockerfile) for an example with Python Poetry and the [beefeater Dockerfile](../../go/beefeater/Dockerfile) for an example with Go, including localproject dependencies.

### Exclude with .dockerignore

A `.dockerignore` file allows you to exclude files from the build context, eliminating the need for rebuilds when files unrelated to the build are changed. This file must be located in the docker build context root.

See [MCM's dockerignore file](../../go/mcm/.dockerignore) for an example.

### Use COPY --chmod

When copying files into your Docker image, use the `--chmod` flag to set appropriate file permissions during the copy operation. This is significantly faster than running `chmod` as a separate RUN command.

Example of using COPY with permissions:

```dockerfile
COPY --chmod=755 ./scripts/entrypoint.sh /entrypoint.sh
```

## How to test locally

Testing local changes to a docker image which is used by a minikube pod (e.g. the model build pipeline or b10cp) requires a few extra steps. First, update your docker env to the minikube registry to allow the image to be resolved inside the cluster:

```sh
eval $(minikube docker-env)
```

Then, run the moon build command with the `ADD_LOCAL_TAG` environment variable flag set to `1`:
```sh
ADD_LOCAL_TAG=1 moon run <project>:build_docker
```

The docker output should include a line with: `naming to docker.io/baseten/<project>:local done`.

Finally, update code references to the docker tag to use the `local` tag. For example:
- For `baseten/model-deploy-util` image, set `MODEL_DEPLOY_UTIL_IMAGE_URI = "baseten/model-deploy-util:local"` in `baseten/settings/local_base.py`
- For `b10cp`, set `b10cp_proxy_image: str = "baseten/b10cp:latest"` in `operator/core/settings/local.py`.

Then, when the image is referenced in minikube, you should be able to see the `local` tag in use. To update the image again, just rerun the build command.

## References

- [Best practices from Docker](https://docs.docker.com/build/building/best-practices/)
- [Docker CIS Benchmark](https://www.aquasec.com/cloud-native-academy/docker-container/docker-cis-benchmark/)
