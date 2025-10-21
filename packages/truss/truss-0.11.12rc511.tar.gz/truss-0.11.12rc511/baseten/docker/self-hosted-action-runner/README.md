# Baseten self-hosted action runner

This directory contains the Dockerfile for the self-hosted action runner used for our GitHub actions [self-hosted runner sets](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners). It's based on https://github.com/actions/runner/

## How to build

From this directory:

```sh
# Credentials in 1Password
docker login -u basetenservice
# Check for latest version number on https://hub.docker.com/repository/docker/baseten/self-hosted-action-runner/tags
docker buildx build --platform=linux/amd64 . -t baseten/self-hosted-action-runner:[new version] --push
```

Then update the image tag used in the runnerset spec here: https://github.com/basetenlabs/baseten-deployment/blob/main/baseten-infra/gh-self-hosted-runner/spec.tftpl

## How to build gpu image

From this directory:

```sh
# Credentials in 1Password
docker login -u basetenservice
# Check for latest version number on https://hub.docker.com/repository/docker/baseten/self-hosted-action-runner-gpu/tags
docker buildx build --platform=linux/amd64 . -t baseten/self-hosted-action-runner-gpu:[new version] --push --build-arg ENABLE_GPU=true
```

Then update the image tag used in the runnerset spec here: https://github.com/basetenlabs/baseten-deployment/blob/main/baseten-infra/gh-self-hosted-runner/gpu-spec.tftpl

## ⚠️ GitHub support policy

GitHub has an [aggressive policy](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/autoscaling-with-self-hosted-runners#controlling-runner-software-updates-on-self-hosted-runners) of deprecating support for old runner versions soon after a new version is released. Once a version is deprecated, runners will fail to connect to GitHub and all workflow runs on the runners will hang.

When this happens, update the first line of the Dockerfile with the latest version, which you can find [here](https://github.com/actions/runner/pkgs/container/actions-runner), and follow the instructions above to build and push the new image.

After updating the images, delete any existing `ephemeralrunners` from the basetensors-infra cluster since the failed runners will prevent new runners from being created:

```sh
kubectl delete ephemeralrunners -n arc --all
```
