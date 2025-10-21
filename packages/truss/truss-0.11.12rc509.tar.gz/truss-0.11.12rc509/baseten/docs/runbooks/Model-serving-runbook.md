# Model serving runbook

## Overview

Model services are defined and built in docker and designed to wrap client models for serving in our kubernetes cluster. The specification for models is thru `kfserving` and defined in code.

## Scalability and Performance

The deployments leverage knative/kfserving scalability dependent on incoming request which are broadly tuned for each model framework. The initial definitions are [here for limits and requests](/backend/oracles/model_deployer/services.py#L68)

### Modifying resources for an existing model deployment
Go to the django admin page to add a `OracleDeploymentSpec`:
* for staging: https://app.staging.baseten.co/billip/oracles/oracledeploymentspec/add/
* for production: http://app.baseten.co/billip/oracles/oracledeploymentspec/add/

Make all the adjustments necessary and click `Save`. This will create a new `OracleDeploymentSpec` from the values specified and will automatically redeploy the model, updating all of its associated versions.


### Rebuilding Docker Images and patching Existing Deployments that will force redeploy
To rebuild an image from the latest code or artifacts run the following from a `shell_plus`:
```
from oracles.model_deployer.services import build_and_deploy_model
build_and_deploy_model(ov, gpu_enabled=gpu_enabled, redeploy=True)
```

This will rebuild the docker image, patch the `kfserving` definition, and launch a redeploy.


### Removing existing revisions to allow pending deployments to deploy
In the case where the cluster is resource constrained (most likely when allocating a GPU) the new deployment may be stuck in a `Pending` state because `k8s` cannot schedule it onto free resources because none exist.

e.g. 1 GPU for the following two deployments
```
baseten-model-zq86d3o-predictor-default-dsnfh-deployment-7hb76v   3/3     Running   0          7h46m
baseten-model-zq86d3o-predictor-default-mtv5x-deployment-6l8lv4   0/3     Pending   0          62s
```

To deploy the newer model, delete the revision associated with the previous deployment
```
kubectl -n baseten delete revision baseten-model-zq86d3o-predictor-default-dsnfh
```

At which point `k8s` will unschedule the previous deployment and schedule the new one
```
baseten-model-zq86d3o-predictor-default-dsnfh-deployment-7hb76v   2/3     Terminating   0          7h48m
baseten-model-zq86d3o-predictor-default-mtv5x-deployment-6l8lv4   0/3     Pending       0          2m35s
```
->
```
baseten-model-zq86d3o-predictor-default-mtv5x-deployment-6l8lv4   2/3     Running   0          4m57s
```

This is NOT graceful, but it is the easiest way to update the deployment in resource constrained conditions.

## Common Tasks
### Delete a model from shell_plus
Sometimes while debugging we may end up with models that are stuck in a forever deploying state. These are sometimes also not deletable from the baseten web app. In such cases they can be deleted using shell_plus like so:
```
from django_context_crum import set_current_user
your_user = User.objects.get(username='<your username>')
set_current_user(your_user)

from oracles.services import undeploy_and_delete_model_and_versions
your_oracles = Oracle.objects.all() # make sure you're logged in as the right user
for oracle in your_oracles:
  if not oracle.primary_version.is_deployed:
    undeploy_and_delete_model_and_versions(oracle)
```
