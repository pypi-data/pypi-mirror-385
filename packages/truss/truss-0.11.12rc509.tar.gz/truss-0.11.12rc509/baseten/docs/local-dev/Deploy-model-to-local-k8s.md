# Deploy model to local k8s

Deploying a model on a Baseten workspace running on your local machine or on a codespace is very similar to deploying a model to staging or any other non-production environment.

### Step 0: Get your local Baseten workspace running

Get your Baseten workspace running:
```sh
bin/run_everything.sh
```

Of course, you'll also need Truss installed. It's not included in the poetry setup, and you'll want to manage that dependency separately.

### Step 1: Create an API key in your local workspace

Use any ordinary mechanism within the Baseten UI to create an API key in your local workspace. Save this key for the next step.

### Step 2: Create or edit `~/.trussrc`

Create an entry in `~/.trussrc` like so:

```
[baseten-localhost]
remote_provider = baseten
api_key = 
remote_url = http://127.0.0.1:8000
```

Make sure to paste your API key into the config

### Step 3: Use Truss with specific remote

The standard Truss created by `truss init`, which is a Python echo server, will be sufficient for most testing (model management page, basic logs, metrics, etc).

When deploying and calling your model, run:

```
truss push --remote baseten-localhost ...
truss predict --remote baseten-localhost ...
```

Autoscaling, production deployments, and other model lifecycle features are expected to work as normal with local development.
