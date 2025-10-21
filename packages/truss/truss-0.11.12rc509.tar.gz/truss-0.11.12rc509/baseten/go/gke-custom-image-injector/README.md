GKE custom image injector is a tool that mutates instance groups. It is designed to introduce custom images into GKE clusters.
GKE clusters don't allow changing the default image for node pools. This bypasses that limitation.

#### Dependencies:
- [gcloud](https://cloud.google.com/sdk/gcloud)
- [packer](https://www.packer.io/)
- [go](https://golang.org/)
- [golangci-lint](https://golangci-lint.run/usage/install/#local-installation)
- [jq](https://stedolan.github.io/jq/)
- [shellcheck](https://github.com/koalaman/shellcheck.git)

## Preparation
Run the targets:
* create-test-ref-node-pool
* check-latest-source-image
* fetch-current-metadata
* delete-test-ref-node-pool

The `gke-essentials.sh` script has comments `## b10: ` to indicate a section with changes from the original, and `## END b10` to indicate the end of the changes.

The `container-cache.sh` script is used to pre-load the container images to the boot image. The image tags/sha need to be updated with the correct GKE/application versions.

## Targets

### gcloud-auth

This target authenticates `gcloud` for application-default credentials. It uses the `gcloud auth application-default login` command.
The credentials are stored in the `~/.config/gcloud/application_default_credentials.json`.

```bash
make gcloud-auth
```

### tidy

This target formats code, tidies dependencies, and runs linters using go fmt, go mod tidy, and golangci-lint, respectively.

```bash
make tidy
```

### create-test-ref-node-pool
This will create a GKE nodepool with all the standard configuration, which also contains the data that we need to update our config.
```bash
  make create-test-ref-node-pool ENV=<environment>
```
#### Required Variables
- `ENV`: The environment for which to mutate instance groups. (`dev`, `staging`, `production`)

### check-latest-source-image
This will check that the latest image from the nodepoool created by `create-test-ref-node-pool` is the image currently declared on your environment.
```bash
  make check-latest-source-image ENV=<environment>
```
#### Required Variables
- `ENV`: The environment for which to mutate instance groups. (`dev`, `staging`, `production`)

### fetch-current-metadata
It will fetch the metadata from the instance pool -> instance group; created by: `create-test-ref-node-pool` 
```bash
  make fetch-current-metadata ENV=<environment>
```
#### Required Variables
- `ENV`: The environment for which to mutate target cluster. (`dev`, `staging`) Value maps to `vars/<env>.json`.


### build-boot-disk
This is the target that builds the packer image for a given environment

```bash
  make build-boot-disk ENV=<environment> RUN_ID=<run_id>
```

#### Required Variables
- `ENV`: The environment for which to mutate instance groups. (`dev`, `staging`, `production`)
- `RUN_ID`: The unique run ID for the mutation. Use an autoincrement unsigned integer.


### list-node-pools
Lists node pool to the env that you're working on
```bash
  make list-node-pools ENV=<environment> 
```

#### Required Variables
- `ENV`: The environment for which to mutate instance groups. (`dev`, `staging`, `production`)

  
### mutate-instance-groups
This target mutates instance groups based on the specified configuration. It uses the go run command to execute a Go application.

```bash
make mutate-instance-groups ENV=<environment> RUN_ID=<run_id> [INSTANCE_GROUPS=<group1>,<group2>]
```

#### Required Variables
- `ENV`: The environment for which to mutate instance groups. (`dev`, `staging`, `production`)
- `RUN_ID`: The unique run ID for the mutation. Use an autoincrement unsigned integer.

### rollback-instance-groups (Not compatible kube-env mutation, if you modified kube-env values, check the values under ./node-metadata to modify the kube-env apropriately to do the mutation)
This target mutates instance groups based on the specified configuration. It uses the go run command to execute a Go application.

```bash
make rollback-instance-groups ENV=<environment>
```

#### Required Variables
- `ENV`: The environment for which to mutate instance groups. (See `/vars` for all the environments)

### Notes
- The `build-boot-disk` target is not idempotent. It will create a new image every time it is run.
- The `mutate-instance-groups` target is idempotent. It will only mutate instance groups that have not been mutated before.
- Office subnet allows ssh access from the office network. 
- A100 instance types are excluded since they are a scare resource. 
- `ENV` and `RUN_ID` are required variables for both targets. They need to be upper-case.
- Values to be replaced in kube-env can be found in `vars/_kube-env.yaml`
- When manually run, the `build-boot-disk` job will update the `last_run_id` value in the `${ENV}` file. And `mutate-instance-groups` target checks and make sure the RUN_ID specified is the same in the json variable file.

## Rollout
Once the image is built (using above make commands) and tested, merge the PR. The GitHub Action `Go Build Test Push` should build an image `gke-custom-image-injector` with a tag in the format `production-<sha>-<timestamp>`. Get the image URI from docker hub or the GH Action output, then update the `run_id` and `gke_custom_image_config` values in the tfvars file for each cluster in `baseten-deployment` repo. Deploy `baseten-deployment`


## TODO's:

* Remove most of the contents of configure.sh
* Organize metadata into files

## Recommended models for testing: 
* [whisper-v3-truss](https://github.com/basetenlabs/truss-examples/tree/main/whisper/whisper-v3-truss) (With L4 and T4)

* [llama-3_1-8b-instruct](https://github.com/basetenlabs/truss-examples/tree/main/llama/llama-3_1-8b-instruct) (H100, needs to be tested on prod with reservation see [release plan](https://www.notion.so/ml-infra/GKE-Image-Mutator-Rollout-15391d2472738046a590cff613572fdc))

