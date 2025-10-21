# Local development

There are currently two options for developing locally:

- [Containerized env](#containerized-env)
- [Directly on laptop](#running-directly-on-laptop)

# Running directly on laptop

## Clone Respository

Run command below. If prompted for password, put personal access tokens instead. You can find personal access tokens from Settings -> Developer Settings -> Personal access tokens

```sh
git clone git@github.com:basetenlabs/baseten.git
```

From the cloned repository directory, install and pull from Git LFS (Large File Support):

```sh
git lfs install
git lfs pull
```

## Install Docker Desktop

Install from here: https://www.docker.com/products/docker-desktop/

## Install your favorite text editor

- Instructions to set up project in [VSCode] [vscode.md](vscode.md)
- Instruction to set up project in [Pycharm](pycharm.md)

## Initial installation

⚠️ Make sure to pay careful attention to the output of each command to ensure it completes without error. Errors can sometimes be hidden in the middle of the output.

## Prerequisite tools

We use [asdf](https://asdf-vm.com/) to easily manage python and nodejs versions, [poetry](python-poetry.org/) is used to manage python env and dependencies.
We use [proto] (https://github.com/moonrepo/proto) to manage our tooling. To install proto and proto tools, run the following command in the root of the monorepo:
```bash
bash <(curl -fsSL https://moonrepo.dev/install/proto.sh)
proto install
```
The usage of asdf is deprecated, use proto if you need to install new tool.

## 🌓 Moon Monorepo

Moon is a fast task runner for monorepos, used for CI, local development, and build artifact generation. For more info, see [this doc](/docs/tools/moon.md).

### Install xcode command line tools (git, llvm, ...)

```sh
xcode-select --install
```

### Postgresql && OpenSSl

```sh
brew install postgresql@15 openssl hdf5 kubectl minikube helm helmfile loki screen
helm plugin install https://github.com/jkroepke/helm-secrets
helm plugin install https://github.com/databus23/helm-diff
```

### Install python, poetry and node through asdf

```sh
brew install asdf
```

#### For zsh

```sh
echo -e "\n. $(brew --prefix asdf)/libexec/asdf.sh" >> $HOME/.zshrc && source $HOME/.zshrc
```

#### For fish

```sh
echo -e '\nsource '(brew --prefix asdf)'/libexec/asdf.fish' >> $HOME/.config/fish/config.fish:
```

### Install plugins

```sh
asdf plugin add python
asdf plugin add poetry
asdf plugin add nodejs
asdf install python
asdf install
```

## Install Dependencies

From the `baseten` repository directory:

```sh
HDF5_DIR="$(brew --prefix hdf5)" GRPC_PYTHON_BUILD_SYSTEM_ZLIB=true poetry install
npm install # If this fails with errors, try: rm -rf node_modules && npm install
```

## AWS setup (optional)

Set up aws-vault accorging to [AWS & Terraform Setup](./AWS-%26-Terraform-Setup.md). This is only required if you need to interact directly with Amazon AWS.

## Patch Minikube (M1)

If you have an M1 Mac and a minikube version is > 1.23.0 and < 1.26.0, your minikube installation has an issue that prevents the cluster from being saved on shutdown. See this [Slack thread](https://basetenlabs.slack.com/archives/C014JUXFGLU/p1645627484572429) for more context. The fix is to update minikube to 1.26.0, which is available in brew:

```sh
brew update
brew upgrade minikube
```

This patch should no longer be necessary with minikube version >= 1.26,0. To check the your minikube version, run:

```sh
minikube version
```

## Initialize database

```sh
./bin/create_dev_db
```

## Set Up local k8s cluster (minikube)

Check Docker Desktop: Preferences -> Resources to make sure you have at least 6 CPUs and 8.5GB of RAM allocated to Docker.
Then run:

```sh
bin/local_cluster_setup
```

Note: based on the configuration of your dev machine, you may need to adjust the cpu and memory settings on line #29 in [`bin/local_cluster_setup`](../../bin/local_cluster_setup) file.

You can now use `minikube stop` and `minikube start` to stop and start your cluster. If your cluster ever gets into a bad state, you should run `bin/local_cluster_setup` again.

## App Setup

### Prepare

```sh
brew services start postgresql@15
cp backend/baseten/settings/local.py.example backend/baseten/settings/local.py
cp backend/.env.example backend/.env
```

#### Start a minikube tunnel

This needs to be done in a different terminal, as the tunnel needs to stay up. Note that `dev_common.sh` (gets called from `create_dev_db` and `local_cluster_setup`) will create the tunnels from `screen`, so you may need to terminate those sessions.

```sh
./bin/dev_run_istio
```

This outputs something like:

```sh
🏃  Starting tunnel for service istio-ingressgateway.
|--------------|----------------------|-------------|------------------------|
|  NAMESPACE   |         NAME         | TARGET PORT |          URL           |
|--------------|----------------------|-------------|------------------------|
| istio-system | istio-ingressgateway |             | http://127.0.0.1:56801 |
|              |                      |             | http://127.0.0.1:56802 |
|              |                      |             | http://127.0.0.1:56803 |
|--------------|----------------------|-------------|------------------------|
http://127.0.0.1:56801
http://127.0.0.1:56802 <<<<< THIS ONE
http://127.0.0.1:56803
```

#### Back to the original terminal

```sh
export MINIKUBE_SERVING_HOST=localhost
export MINIKUBE_SERVING_INGRESS_PORT={the port corresponding to THIS ONE above, eg 56802}
```

In order to run pynodes and models, the **minikube tunnel must be up** and the environment variables must also be up/set when running the django app.

## Commit hooks

```sh
# Install precommit hooks
# To skip hooks to run on certain commit you can:
# git commit -n ... or git commit --no-verify ...
poetry run pre-commit install
```

## Start the application

Check the section for your CPU architecture (M1 or not) and follow the steps. You should be able to open http://localhost:8000/ in a browser and login with `baseten:baseten`

### Terminal 1

```sh
bin/dev_run_django
```

### Terminal 2

```sh
bin/dev_run_node
```

## Verifying everything works

⚠️ Before starting, run `kubectl get pods --all-namespaces` and ensure that all `STATUS`'s are `RUNNING` or completed.

Go to http://localhost:8000/ and log in using username `baseten` and password `baseten`.

### Deploy a model

With the Baseten application running locally, you can deploy a simple model truss following the quickstart guide [here](https://truss.baseten.co/quickstart), with some caveats:

- To avoid conflicts between the Truss python package and the Baseten monorepo, you should run your truss commands in a separate shell, ideally inside a python [venv](https://docs.python.org/3/library/venv.html).
- Before deploying the truss, you'll need to manually configure your remote using the instructions [here](https://truss.baseten.co/remotes/baseten#set-the-remote-manually):
  - The `remote_url` will be `http://localhost:8000/`
  - The `api_key` can be generated at https://localhost:8000/settings/api_keys
  - The `remote_name` is still `baseten`

Verify that the model deploys successfully. Now, let's make sure the model is running properly by invoking it.

### Invoke the model

With the Baseten application running locally, navigate to the page of the model you deployed in the first step. You can invoke the model via the "Call model" dialog, either directly in the browser or following the integrate instructions to call it programmatically.

## Installing shell aliases

You can install useful aliases for baseten application development as well as interacting with kubectl by running:

```
./bin/install_aliases.sh
```

Take a look at (baseten_aliases.sh)[../../bin/baseten_aliases.sh] to see what aliases are available.

# Containerized Env

## Prerequisites

- Docker desktop, highly recommend at least 8 CPU and 16GB memory allocated in resources
- Logged into Docker Hub locally, using credentials from 1Password.
- Dev container secrets at `.devcontainer/secrets.env`, can find in 1Password under `Devcontainer Secrets` in shared engineering vault

## Usage

- `./bin/dev_environment.sh create` - Creates an entirely new containerized env locally
- `./bin/dev_environment.sh attach` - Attaches to an existing containerized env
- `./bin/dev_environment.sh stop` - Stops an existing container (brings down resources, processes, etc)
- `./bin/dev_environment.sh restart` - Restarts an existing container
- `./bin/dev_environment.sh delete` - Deletes an existing container

## Development

The monorepo is mounted by default at `/workspace`, so you can use your local editor on your machine and changes will be
reflected instantly in the container. Git credentials are proxied through your machine's ssh agent, so that should be seamless.

### MacOS Virtual File Sharing

For optimized performance on the filesystem mount if you're running Docker Desktop, you can setup synchronized file shares via
Resources -> File Sharing. There, if you create a new share pointed to your monorepo directory, you'll have _much_ better
performance when syncing files bidirectionally from host<->container.
