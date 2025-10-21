# Model Zoo Automation Rollout

Roll out model zoo automation model by model. For each model the following
procedure should be followed.

## Prerequisites

1. Model zoo automation mechanism to deploy models should be functioning
   correctly. - Done (by Nish)
2. Dynamic setting mechanism to deploy model as a copy or otherwise - described
   below

  - Make sure this is well tested in advance

3. Hash checking mechanism is in place to avoid deploying duplicate copies. - In
   progress (Abu)
4. Extra resources are provisioned in the cluster to support both new and old
   models. Note that many models need gpu.
5. Forward and revert scripts for switching user models are created and tested.

## Dynamic setting mechanism

(In progress) - Pankaj

Store a dictionary under automaticallyDeployedModelZooModelsWhitelist

Key should be the model zoo model name and value should be another dictionary
with only one key called copy.

When copy is True, the model should deploy as a model zoo model called
`{model_zoo_name}_copy`. When copy is False, the model should as a new version
of existing model zoo model (or create one if needed, e.g. in dev during
testing).

## Individual Model Rollout

Do the whole procedure first on staging and then on prod.

Proceed as follows for an individual model on an individual environment.

### Add code to baseten repo under truss_models

truss folder name should initially be the same as corresponding model zoo model.

### Enable model zoo automation for this model but as a copy

Set the dynamic setting to add model zoo automation for the model. Initially set
copy to true.

Do this by modifying the `baseten-django-dynamic-settings` configmap directly.

```
kubectl edit cm -n baseten baseten-django-dynamic-seetings
apiVersion: v1
data:
  ratelimitEnabled: "true"
  automaticallyDeployedModelZooModelsWhitelist: '{"iris": {"copy": true}}'
  modelZooDeploymentAutomationEnabled: "true"
kind: ConfigMap
metadata:
  name: baseten-django-dynamic-settings
  namespace: baseten
```

You may need to define secrets for the admin organization if the model needs it.

### Test the model zoo model

Model zoo automation should pick this up and create a model zoo model named
f'{model_zoo_name}_copy'.

Test this as follows:

1. Create an application that uses the corresponding current model zoo model in
   any account you want to use for testing.
2. From shell_plus, manually point the oracle version on the user side to the
   new model zoo model.
3. Make sure the application works correctly as before.

```
import crum
user = User.objects.get(email='useremail@bla.com')
crum.set_current_user(user)
oracle = Oracle.objects.get(pk='[model_id]')  # Get this id from baseten ui of the user
oracle_version = oracle.current_version
print(oracle_version.proxy_model_version_id)  # This should be the current model zoo model version 
oracle_version.proxy_model_version_id = new_oracle_version_id  # version id of the copy model that was deployed
oracle_version.save()
```

### Rollout as new version of model zoo model

Set copy to false for the model in dynamic settings. This should deploy the
model as a new version of the model zoo model.

This would mean that all new applications for the model zoo model will point to
the new model but existing applications will continue to point to the old
version.

### Test the new model zoo model with a new application

Create a new application that uses the model zoo model. Make sure the
application works as expected.

Check that the oracle version on the user side points to the new model zoo model
version.

```
import crum
user = User.objects.get(email='useremail@bla.com')
crum.set_current_user(user)
oracle = Oracle.objects.get(pk='[model_id]')  # Get this id from baseten ui of the user
oracle_version = oracle.current_version
# Make sure this prints id of the new model zoo model version
print(oracle_version.proxy_model_version_id)
```

### Migrate existing applications to the new model version

Make sure to take a note of the old model zoo oracle version. Make sure a
rollback script is ready to point applications back to the original version. The
revert script should migrate all oracles pointing to the new model zoo version
to the old one.

```
import argparse
import sys
from oracles.models import OracleVersion 

MAP_OF_NEW_ZOO_TO_OLD_ZOO_IDS = {}

def rollback(new_model_zoo_id: str):
    """
    Takes the new model zoo id (truss version) and sets all model versions equal to the new one,
    to the old model version located in MAP_OF_NEW_ZOO_TO_OLD_ZOO_IDS
    """
    affected_model_versions = []
    old_model_zoo_id = MAP_OF_NEW_ZOO_TO_OLD_ZOO_IDS[new_model_zoo_id]
    user_model_versions = OracleVersion.objects.filter(proxy_model_version_id=new_model_zoo_id)

    for user_model_version in user_model_versions:
        user_model_version.proxy_model_version_id = old_model_zoo_id
        user_model_version.save()
        affected_model_versions.append(user_model_version.id)

    return affected_model_versions


parser = argparse.ArgumentParser(
    description="Rollback model versions from new model zoo to old model zoo version"
)
parser.add_argument("-id", type=str, help="the new model zoo id to replace", required=True)
args = parser.parse_args()
new_model_zoo_id = args.id

if new_model_zoo_id not in MAP_OF_NEW_ZOO_TO_OLD_ZOO_IDS:
    print("That ID does not exist")
    sys.exit()

affected_versions = rollback(new_model_zoo_id)
print(affected_versions)

```

With that, run the forward migration script to point existing applications,
across all users, to the new oracle version.

```
import argparse
import sys
from oracles.models import OracleVersion

MAP_OF_OLD_ZOO_TO_NEW_ZOO_IDS = {}

def forward(old_model_zoo_id: str):
    '''
    Takes the old model zoo id (non truss) and sets all model versions to the 
    new one located in MAP_OF_OLD_ZOO_TO_NEW_ZOO_IDS
    '''
    affected_model_versions = []
    new_model_zoo_id = MAP_OF_OLD_ZOO_TO_NEW_ZOO_IDS[old_model_zoo_id]
    user_model_versions = OracleVersion.objects.filter(proxy_model_version_id=old_model_zoo_id)

    for user_model_version in user_model_versions:
        user_model_version.proxy_model_version_id=new_model_zoo_id
        user_model_version.save()
        affected_model_versions.append(user_model_version.id)
    
    return affected_model_versions


parser = argparse.ArgumentParser(
    description="Forward model versions from old model zoo to new model zoo version"
)
parser.add_argument("-id", type=str, help="the old model zoo id to replace", required=True)
args = parser.parse_args()
old_model_zoo_id = args.id

if old_model_zoo_id not in MAP_OF_OLD_ZOO_TO_NEW_ZOO_IDS:
    print("That ID does not exist")
    sys.exit()

affected_versions = forward(old_model_zoo_id)
print(affected_versions)

```


Make sure the forward and revert scripts are tested well.

### Delete the old model zoo version

A few days after everything is known to function ok
