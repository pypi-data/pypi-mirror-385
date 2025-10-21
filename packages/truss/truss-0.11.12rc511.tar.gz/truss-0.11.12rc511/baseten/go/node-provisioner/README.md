> **Note: Cluster autoscaling via `NodeProvisioner`s is a WIP! See [Linear](https://linear.app/baseten/project/node-pool-management-db37d5e59b5f/issues) for the current state of the project and planned improvements.**

The `node-provisioner` project is a minimal implementation of cluster autoscaling via a `NodeProvisioner` CRD and controller. It is meant to support autoscaling for node pools and/or cloud providers that aren't supported by the [kubernetes cluster autoscaler](https://github.com/kubernetes/autoscaler). It is not meant to comprehensively reimplement all of the cluster autoscaler functionality; in the future, this logic might get moved into cluster autoscaler or another project.

The `NodeProvisioner` controller was built using the [`operator-sdk`](https://sdk.operatorframework.io/docs/overview/) / [`controller-runtime`](https://github.com/kubernetes-sigs/controller-runtime) library.

# Limitations

The following features are not yet implemented:
* Migrate to cdli and flux-cd ([ticket](https://linear.app/baseten/issue/BT-14634/cicd)).
* Support for cloud providers aside from GCP (e.g. [ticket for supporting Crusoe](https://linear.app/baseten/issue/BT-14484/implement-crusoe-logic-for-node-scale-up-down)).
* Provisioning nodes based on a max utilization threshold ([ticket](https://linear.app/baseten/issue/BT-14630/scale-up)).
* Automatic node defragmentation ([ticket](https://linear.app/baseten/issue/BT-14631/defrag)).
* Automatic rotation of DWS nodes ([ticket](https://linear.app/baseten/issue/BT-14629/dws-rotation)).
* Creating node pools and/or instance groups ([ticket](https://linear.app/baseten/issue/BT-14632/creating-instance-groups)). Currently, the `NodeProvisioner` can only manage capacity for existing instance groups.
* Managing capacity across multiple instance groups ([ticket](https://linear.app/baseten/issue/BT-14799/support-multiple-instance-groups)).

See [Linear](https://linear.app/baseten/project/node-pool-management-db37d5e59b5f/issues) for a more updated status.

# Project structure

While `operator-sdk` provides a lot of scaffolding for `node-provisioner`, `node-provisioner` has diverged slightly from the common [operator-sdk project layout](https://sdk.operatorframework.io/docs/overview/project-layout) in order to integrate with our codebase / development practices.

Summary of the main directories in `node-provisioner`: 
* [`api`](/go/node-provisioner/api/) contains the schema for the `NodeProvisioner` CRD (see `nodeprovisioner_types.go`).
* [`cmd`](/go/node-provisioner/cmd/) contains the entrypoint for the node provisioner controller.
* [`internal`](/go/node-provisioner/internal/) contains the core logic for scaling node pools. For more details, see the [README](/go/node-provisioner/internal/README.md).

Unlike standard go `operator-sdk` projects, the manifests for `node-provisioner` are managed / packaged by Helm to be compatible with our Helm CI / CD pipeline. These manifests live in [`/helm/charts/node-provisioner`](/helm/charts/node-provisioner/), similar to other Baseten projects.

# Development

## Updating the `NodeProvisioner` schema

Updates to the `NodeProvisioner` should be made to `nodeprovisioner_types.go`. `nodeprovisioner_types` uses kubebuilder markers for automatically generating kubernetes manifests (so do other files in this project--e.g. RBAC markers in `nodeprovisioner_controller`). To update manifests and other generated code, run:
```
moon run node-provisioner:manifests
moon run node-provisioner:generate
```

For more details, see:
* [operator-sdk docs](https://sdk.operatorframework.io/docs/building-operators/golang/tutorial/#define-the-api) on defining APIs
* [kube-builder docs](https://book.kubebuilder.io/reference/markers) on markers

## Manual deployment
TODO: update instructions once migrated to cdli.

1. Build and push the node provisioner operator. This command will push the docker image to `baseten/node-provisioner:{branch}-{sha}-{time}`:
```
moon run node-provisioner:build_docker
```
Then push to docker.

2. Deploy to the cluster with helm:
```
IMAGE_TAG={image_tag} moon run node-provisioner:helm_upgrade
```

Run `moon run node-provisioner:helm_uninstall` to uninstall the helm chart.

## Adding `NodeProvisioner`s

Unfortunately, `NodeProvisioner`s are not currently defined in terraform / flux. See `wp-gcp-us-central1-dev`, `us-central1-prod-1`, and `us-east4-prod-1` for examples of `NodeProvisioner`s (`kubectl get nodeprovisioners`).

Since `NodeProvisioner`s can only manage existing instance groups in GCP, setting up a node pool to be managed by the node provisioner controller involves two steps:
* Updating the node pool in terraform to set the `nodeprovisioner.compute.baseten.co/provisioner-name` label. Our current convention is to set this to the node pool name.
* Defining the `NodeProvisioner` manifest.
    * Set `name` to the value of the `nodeprovisioner.compute.baseten.co/provisioner-name` label.
    * Set `existingInstanceGroupNames` to the instance group name (note that this is a list field, but multiple instance groups are not yet supported--see [this ticket](https://linear.app/baseten/issue/BT-14799/support-multiple-instance-groups)).
    * Set the `minGPUUtilizationPercent` and/or `minUnutilizedGPUNodes` based on the node pool's scaling requirements.

# Links
* [internal/README.md](/go/node-provisioner/internal/README.md): for more implementation details of the `NodeProvisionerReconciler`, which is the controller for the `NodeProvisioner` CRD.
