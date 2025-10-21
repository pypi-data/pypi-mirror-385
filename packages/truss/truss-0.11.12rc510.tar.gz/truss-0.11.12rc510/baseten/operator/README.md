# Workload plane operator

Endpoints are defined in `core/api.py`. Consider using https://fastapi.tiangolo.com/tutorial/dependencies/ as we expand out the endpoint functionality.

As we build out integrations, please use https://fastapi.tiangolo.com/advanced/generate-clients/ for client interactions with this API

# Development


The preferred and supported method is using the devcontainer.

Operator uses `moon` like all other components. This manages the `venv` and `uv` etc. 

## Tests

Check out `test_api.py` and `test_server.py` for how to test the raw endpoints and the running ASGI container. Most tests should probably only need to use methods from `test_api.py`

To run tests
```shell
# Moon
moon operator:test

# Moon with pytest args passed
moon operator:test -- --verbose

# Directly with pytest
uv run pytest tests
```

## Check k8s namespace baseten-ksvc-settings

Check namespace exists (within the devcontainer):

```
kubectl get ns baseten-ksvc-settings
```

Create if needed:

```
kubectl create ns baseten-ksvc-settings
```

## Run api server locally

If running the operator from VS Code (including in a codespace), you should add the `./operator` folder as a separate VS Code workspace root. Open the command palette (Cmd + Shift + P) and select "Add folder to workspace", then navigate to the "operator" folder.

When you open a new VS Code terminal, you'll be asked which folder to use. To run the operator, make sure you select the "operator" folder. Then run:

Running the service

## Moon project information

This project uses moon for task management. To see available tasks, run:

```shell
moon project operator
```

Key tasks include:
- `moon run operator:install` - Install dependencies
- `moon run operator:run` - Run the API server with hot reload
- `moon run operator:devrun` - Run the API server with hot reload and dev friendly output
- `moon run operator:test` - Run tests
- `moon run operator:format` - Format code
- `moon run operator:lint` - Lint code

Here's some extra examples

```shell
# Moon, install deps
moon run operator:install

# Moon, run quietly
moon operator:run

# Moon with service args passed to switch eg. port
moon operator:run -- --port 9090

# Moon with log output
moon operator:run --interactive

# Moon with more dev friendly output (pretty stacktraces, mixed JSON) from logging-dev.conf
moon operator:devrun
```


## Bare metal

Bare metal is not the preferred/supported setup.

### Moon

If developing on bare-metal (not devcontainer/docker), install `moon`.

```shell
# MacOS install moon
brew install moon
```

### minikube

The devcontainer runs a minikube and is the preferred/support option. If you decide to not use the devcontainer, run your own minikube.

```shell
# MacOS install and launch minikube
brew install minikube

# Launch it
minikube start
# 😄  minikube v1.36.0 on Darwin 15.6.1 (arm64)
# ... many emojis later...
# 🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default

# Grab a kubeconfig file
kubectl config set-context minikube
kubectl config view --raw > ~/.kube/minikube.yaml
```

You can now switch clusters using `KUBECONFIG=~/.kube/minikube.yaml` or `kubectl config set-context`

