# ATCtl

_A command line interface for the ATC_

The ATC exposes a gRPC API for managing deployments in the world of multi-cluster models (MCM). This is the main interface between the application level (Django) and the infrastructure (MCM).

ATCtl provides a command line interface for interacting with the ATC for internal development, debugging, and monitoring use cases. It is a wrapper around the gRPC API, providing a more developer-friendly way to view and interact with MCM deployments. It is heavily inspired by `kubectl`.

## Quickstart

The `create-test-deployment` [make target](../../Makefile) creates a test deployment with the necessary namespace and instance type in the local dev environment. You can then use ATCtl to interact with this deployment:

```bash
# From ./go/mcm
make create-test-deployment

# List deployments
atctl get deployment -n org-test
```

Please reference the `create-test-deployment` target for working example commands. You can also find full help and examples for ATCtl by running `atctl --help`.

## Running

### Running on the ATC

ATCtl comes pre-packaged on the ATC image. You can run it like so:

```bash
# Note: you need to get the exact pod name first
kubectl exec -it baseten-mcm-atc-xxx-xxx -n baseten -- atctl -h
```

### Running locally

To install ATCtl locally, from the `./go/mcm` directory, run:

```bash
make install-atctl
```

If you're running minikube locally, atctl will automatically detect the minikube IP and port number to connect to the ATC. If you want to connect to the ATC running in a cloud environment, you can run:

```bash
kubectl port-forward -n baseten svc/baseten-mcm-atc 51002
# ATC will automatically try localhost:51002
atctl --help
```

If the ATC is reachable at a different address, you can specify it with the `--host` flag:

```bash
atctl --host example.com:8000
```

## Development

If making changes to ATCtl, you can compile and run it in one command with:

```bash
go run ./cmd/atctl --help
```

### Code structure

All the code for ATCtl lives under this directory. All the commands are defined in the `cmd` directory. Many of the commands are supported by corresponding files in the `controller` directory. You can think of `cmd` as the user interface and `controller` as the code that knows how to call the gRPC API.

The `resources` directory contains information about the resources (deployment, namespace, instance type) that ATCtl can interact with. Note that the command code is generally resource-agnostic. The configuration for each resource is defined under `resources/options.go`.

## Integration tests

[`atctl_test.go`](../../services/v1/integrationtest/atctl_test.go) contains end-to-end integration tests for ATCtl. These tests are run as part of the [mcm-integration-tests](../../../../.github/workflows/mcm-integration-tests.yml) GitHub Action.
