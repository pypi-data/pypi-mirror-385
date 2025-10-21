# Baseten Knative-Serving Fork

## Repo and Branches
Baseten's knative repo is at https://github.com/basetenlabs/knative-serving
- We use the `baseten` branch for workload plane clusters (GCP).
- We use the `baseten-knative-1-7-4` branch for the legacy AWS cluster.


## Development in Codespace
It is better to develop and test in codespace because the frontend/backend/minikube runs better in codespace.
This way we can test E2E with model deployments with knative.

## Setting up codespace
Use the baseten repo to create a new workspace. This will setup the environment needed to run the frontend/backend/minikube.

Next create clonse of the baseten knative repo and build an image:
```bash
cd /workspaces
git clone git@github.com:basetenlabs/knative-serving.git
cd knative-serving
git checkout baseten
go install github.com/google/ko@latest

# Add to ~/.bashrc
export PATH=$PATH:/usr/local/go/bin:~/go/bin

eval $(minikube docker-env)
export KO_DOCKER_REPO=ko.local
ko build ./cmd/autoscaler/
```

This should push an autoscaler image to docker on minikube. Note the name of the image.

Next we use the image for a knative component e.g. autoscaler:
```bash
kubectl edit deploy autoscaler -n knative-serving
```

- Update the `image:` there to the image above (existing one would be gcr.io...)
- Check that the autoscaler pod comes up fine

```bash
kubectl get logs -n knative-serving
```

- Verify pod's logs to make sure there are no errors

Now you have a dev loop in place. You can make code changes, build new image and update it in the autoscaler deployment.

## Running PodWatcher in Codespace
PodWatcher is a service that we use to watch for dynamic settings for a model (configmap) and then apply the changes to the relevant Knative API resource e.g. updating stable window for a model deloyment we patch PodAutoscaler with an updated annotation `autoscaling.knative.dev/window`

To run PodWatcher, in a terminal, go to baseten repo under go/kube-watcher/ folder, run: `make run-pw-local`


## Pushing knative branch to Github
The codespace instance is created using the baseten repo thus the generated token will only have read-only access to other repos (github limitation).

To push a local branch to the Github repo, you will need to setup to use SSH.
- Create SSH key in the codespace: `ssh-keygen -t ed25519 -C "will.lau@baseten.co"`
- Add the SSH key to the agent: `ssh-add ~/.ssh/id_ed25519`
  - If that does not work try restarting the agent: `eval "$(ssh-agent -s)"`
- Add the public key to your Github account

Next we to make sure that the local repo is setup to use SSH and not HTTPS. You can check this by running `git remote -v`. If the origin URI is is prefixed with git@ then it is SSH, otherwise it would be https.

To update to use SSH use the command: `git remote set-url origin git@github.com:basetenlabs/knative-serving.git`

Then run `git remote -v` to verify that it is in effect.

The current baseten codespace has a git global config that overrides any SSH into HTTPS, so you might have to disable this. Edit the global config using: `git config --global --edit`

## Pushing image to ECR
Currently, the custom knative images are push into our public ECR repo: `public.ecr.aws/q8h3f2p1`

All env(dev/staging/prod) use this repo for knative images.

In order to push an image from codespace into ECR, you will need to setup aws-vault using the [guide here](https://github.com/basetenlabs/baseten/blob/8f665037feadda43d3bb4b12f861053a2ce5c92b/docs/local-dev/AWS-%26-Terraform-Setup.md).

A summary of the commmands to setup aws-vault:
```
# install
asdf plugin-add aws-vault https://github.com/karancode/asdf-aws-vault.git
asdf install aws-vault latest
asdf global aws-vault latest

# configure
aws configure
aws-vault add profile_name --backend=file
```

Once aws-vault is setup, you can then push the image using the prod role:
```
# AWS prod role
aws-vault exec prod-admin --backend=file

# Login to ECR repo and get token
aws ecr-public get-login-password --region us-east-1 > ecr.txt

# Use token for docker login to repo
cat ecr.txt | docker login --username AWS --password-stdin public.ecr.aws/q8h3f2p1

# Tag the local image.
docker tag ko.local/autoscaler-12c0fa public.ecr.aws/q8h3f2p1/baseten/knative-autoscaler:v0.0.5-1.7.4

# Push image to ECR
docker push public.ecr.aws/q8h3f2p1/baseten/knative-autoscaler:v0.0.5-1.7.4
```

## Changing log level
Logging level at the component granularity can be made through the config-logging configmap: `k describe configmap config-logging -n knative-serving`

Edit the configmap: `k edit configmap config-logging -n knative-serving`

Copy the relevant line from the example and paste it directly under the `data` element e.g. to enable debug level for autoscaler we add `loglevel.autoscaler: "debug"` 


## Test in DEV
The quickest way to test in DEV is to use `kubectl edit deployment` on the DEV cluster and update the image directly.


## Deploy to Dev/Staging/Prod
- For AWS Legacy Cluster, update the helm chart in `baseten` repo and make sure to use image build from the knative `baseten-knative-1-7-4` branch
- For new workload plane clusters (GPC). update the TF variables in `baseten-deployment` repo and make sure to use the image build from the knative `baseten` branch.

## Adding new dependencies
- Add package to go.mod
- Run: `go get -u ./...`
- Run: `go mod tidy` (this updates go.sum)
- Run: `go mod vendor` (this updates vendor/modules.txt)
