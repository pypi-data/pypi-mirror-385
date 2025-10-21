# Baseten kubernetes watchers

This is a collection of watchers that can be used to watch for events in a Kubernetes cluster. The watchers are designed to support the [baseten](https://github.com/basetenlabs/baseten) backend.

## Watchers

### PodWatcher

Used to watch for pod events. It collects events and pod changes relating to creating pods, from scheduling to running. This watcher emits opentelemetry traces for each pod, and prometheus metrics across all pods. To run this watcher, use the command `./pod-watcher` in the docker image. It can be run locally against a remote cluster by setting the `KUBECONFIG` environment variable, otherwise it will use the in-cluster configuration.

PodWatch also performs some coldboost duties. It tags every new coldboost node with a priority based on age. It also deletes coldboost overprovisioning pods if they're not on the primary coldboost node.

### OOMWatcher

Used to watch termination event and/or restarts of Kubernetes events. To run this watcher, use the command `./oom-watcher` in the docker image. It can be run locally against a remote cluster by setting the `KUBECONFIG` environment variable, otherwise it will use the in-cluster configuration.

## Building

To build the docker image, run `make docker-build`.