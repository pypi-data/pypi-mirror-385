# Overprovisioning resources

In order for there to be a buffer of available resources, we create idle workloads that reserve resources in the cluster. These workloads have the lowest possible priority (PriorityClasses = -1) such that the cluster autoscaler will kick in to expand so that they're up. Their low priority is below that of the default (0) for pods that don't have an assigned priority class. Whenever a workload is scheduled onto the cluster and there isn't room for it, the overprovisioning pod will get booted in favor of the other workload, and the lack of room for the overprovisioning pod will trigger a cluster scale up.

## Dumb but predictable

In order to change the amount of resources in the buffer you can simply edit the different deployments in the `overprovisioning` namespace. In the future we could have the number change according to some other mechanism (eg % of cluster size, some predictive model, etc), but for now it is very much just a knob we can turn predictably.

The replica count is not tracked by terraform so your changes do not need to go through review and will not get undone by a production deploy. This is to allow us to quickly expand the cluster to a desired size without the need for a deploy.

Commands to change the number of replicas:

```bash
kubectl scale deployment --replicas=<desired> -n overprovisioning <deployment-name>
```

eg to scale the blueprint gpu buffer (which is a deployment named `blueprint-gpu` in the `overprovisioning` namespace) to 3 replicas:

```bash
kubectl scale deployment --replicas=3 -n overprovisioning blueprint-gpu
```

## Creating a new buffer

To create a new buffer, you'll need to create a new deployment in the `overprovisioning` namespace. This is done via terraform in the `baseten-deployment` repository, under `multi-cluster/workload-plane-<cloud-provider>/<cluster-name>/<cluster-name>.tfvars` by adding to the list in the `overprovisioners` variable. The format is:

```hcl
{
  name = "gpu"
  node_selector = {
    "baseten.co/karpenter-provisioner" = "gpu"
  }  # optional
  gpu      = 1  # optional
  cpu      = "500m"  # optional
  memory   = "1Gi"  # optional
  replicas = 0
},
```
