This image contains majority of the utilities that an engineer needs to interact with k8s clusters.

## Build
From this directory, run
```
docker login -u basetenservice
docker buildx build --platform linux/amd64,linux/arm64 --push -t baseten/k8s-utils .
```

## Included utilities
- bash
- vim
- python3
- jq
- kubectl
- k9s
- openssl
- postgres-client
- aws-cli
- oci-cli
- gcloud

## Client

- Add new `aws-vault` profiles `fde-users` and `oncall` in `~/.aws/config` file. You may need to change the `source_profile` name. That’s the base profile without properties.

  ```bash
  [profile fde-users]
  source_profile=baseten
  duration_seconds=3600
  role_arn=arn:aws:iam::836885557665:role/fde-users

  [profile oncall]
  source_profile=baseten
  duration_seconds=3600
  role_arn=arn:aws:iam::836885557665:role/production-oncall-role
  ```

- Have docker demon started
- Copy the `start.sh` script to a folder
- From the folder, run `sh start.sh` and select the cluster you need to access
  - If you are oncall or infra engineer, add `-u oncall` to the cmd. This gets you cluster admin permissions as well as the GCP compute admin role for the project.
  - Port-forwarding. If you want to do port-forward, add `-p port1,port2` to the startup command, then port-forward inside the container. The ports are accessible on host. The following example enables querying `vmselect` port (8481) and `vmalertmanager` port (9093) from your laptop, The forwarded port must in the `-p` list

## Adding new clusters
- Add a folder under the `clusters`, name it the same as the cluster name.
- Add a `env.sh` to set the `provider`
  - For new providers, modify the `template/bash_profile` accordingly
- Download the kubeconfig file for the cluster and save to the folder
- Upload the updated clusters folder to S3.

  `aws-vault exec prod-admin -- aws s3 cp --recursive clusters/ s3://baseten-workload-plane-templates/fde/clusters`

