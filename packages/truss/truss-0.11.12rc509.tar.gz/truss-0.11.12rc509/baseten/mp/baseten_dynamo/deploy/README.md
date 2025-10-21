# Baseten Dynamo Deployment

## Directory Structure

### `model-chart/`
Previously contained a separate Helm chart specifically for individual model deployments.
This has been moved to `helm/charts/baseten-dynamo-model/`.

### `gateway/`
Previously contained the configmap for the gateway to know which models to route to.
This has been moved to `helm/charts/shared-endpoints-gateway/values.yaml`.

### `model-values/`
Contains the values.yaml for each model.

## Usage
To deploy or update a model, make sure there is a `<model_name>.values.yaml` file in the `model-values/` directory for that model, like `llama4-scout.values.yaml`.
1. `make install_model MODEL_NAME=<model_name>`
2. Follow the prompts to confirm the deployment.

> You can deploy models without the configmap change and then update the configmap later.

To update the gateway, first determine which models should be routeable from the gateway and add them to `gateway/values.yaml` in prod and `gateway/values.dev.yaml` in dev. Run `make update_gateway`.

## A helpful command in case 'diff' is broken

```
helm plugin uninstall diff
helm plugin install https://github.com/databus23/helm-diff
```
