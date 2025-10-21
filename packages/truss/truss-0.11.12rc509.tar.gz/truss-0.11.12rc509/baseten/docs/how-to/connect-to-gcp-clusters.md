# How to connect to GCP clusters

## Step 1: Get access to the GCP projects

You can check if you already have access by going to the [Cloud Resource Manager](https://console.cloud.google.com/cloud-resource-manager) and seeing the list of projects available to you.

There is one project per workload plane, which is currently one per environment:

- production: `production-workload-plane-1`
- staging: `staging-workload-plane-1`
- development: `multi-cluster-gcp`

If you don't already have access and you need it, ask Phil or in #infra.

## Step 2: Install the gcloud CLI

Install the gcloud CLI by running:

```sh
brew install --cask google-cloud-sdk
```

Alternatively, you can also follow the official instructions [here](https://cloud.google.com/sdk/docs/install)

Check that it's installed by running `gcloud version`.

## Step 3: Configure the CLI:

```sh
# Login
gcloud auth login

# Install the gke component
gcloud components install gke-gcloud-auth-plugin
```

## Step 4: Connect to the cluster

You need to do this in each shell to give it access to GKS:

### Option A: Manual commands

```sh
# Select the project based on the desired workload plane environment mapping above (e.g. `production-workload-plane-1` for production)
gcloud config set project <project_name>

# Alternatively, you can set the project name as an environment variable
export CLOUDSDK_CORE_PROJECT=<project_name>

# Get gke credentials
gcloud container clusters get-credentials us-east4-prod-1 --region=us-east4

# You should now be able to access the cluster through kubectl
kubectl get pods -n kube-system
```

### Option B: Shell aliases

If you have the [baseten aliases](../../bin/install_aliases.sh) installed, you can run:

```sh
# connect to the "main" cluster per environment
gkss <dev|staging|prod>
# connect by cluster name
gkss <us-east4-prod-1|us-central1-prod-1|...>
```
