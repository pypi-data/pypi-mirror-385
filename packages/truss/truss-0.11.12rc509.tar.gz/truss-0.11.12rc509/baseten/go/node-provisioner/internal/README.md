# Implementation overview

## `NodeProvisionerReconciler`
`NodeProvisionerReconciler` is a controller for the `NodeProvisioner` CRD. At a high level, it watches for pod events via an informer, which triggers calls to the cloud provider to provision / deprovision nodes. The controller assumes that `NodeProvisioner`s are only set up for **GPU nodes**.

Nodes provisioned by a `NodeProvisioner` are marked with a label containing the provisioner name. When GPU utilization falls below a target, the controller taints empty nodes with a deletion timestamp, and deprovisions tainted nodes after the deletion timestamp.

### Reconcile requests
`SetupWithManager` configures a watcher for pod events, which are handled in **`handlePodEvent`**. There are two cases that trigger a reconcile request:
1. Unschedulable pod. Expect that in reconciliation the node provisioner will scale up nodes.
    * This shouldn't happen with MCM deployments
    * This is possible with non-MCM workloads--e.g. training jobs
2. The pod is associated with an empty node (e.g. pod deleted). Expect that in reconciliation the node provisioner will scale down nodes.

For case (1), a reconcile request is returned for the first provisioner that satisfies the pod's required node affinity and has taints that are tolerated by the pod. This is naive and **does not** account for other factors, e.g. the pod's resource requests ([ticket](https://linear.app/baseten/issue/BT-14498/account-for-non-gpu-resources-when-matching-pods-provisioners) for improving this logic).

For case (2), a reconcile request is returned for the provisioner specified by the provisioner name label on the node.

### Reconciliation loop
Reconciliation is performed in **`Reconcile`**. It consists of two stages:
1. Evaluate the state of the cluster and updates the `NodeProvisioner` status accordingly. This does not make any changes to the cluster.
    * Scale-up case: if there are unschedulable pods, this naively scales up target size by the number of nodes required to satisfy the GPU requests. This **does not** account for other resource types.
    * Scale-down case: if current GPU utilization is less than the min utilization threshold (`MinGPUUtilizationPercent`), set target size to the maximum number of nodes required to meet the min utilization threshold.
        * The `NodeProvisioner` spec also supports an absolute threshold on the number of fully unutilized nodes (`MinUnutilizedGPUNodes`). If set, the reconciler will maintain this buffer even if utilization is below `MinGPUUtilizationPercent`.
2. Reconcile the cluster with the `NodeProvisioner` desired state.
    * If `currentSize < targetSize`, provision more nodes by calling the `CloudProvider` API.
    * If `currentSize > targetSize`, scale down by (1) deprovisioning nodes tainted for deletion where the deletion timestamp has passed, or (2) tainting additional empty nodes for deletion.
    * For simplicity, the reconciler will only perform one action per loop.

#### Example
For simplicity, assume that in these examples nodes are either completely utilized or completely empty; i.e. utilization at the node level == utilization at the chip level.

**Scenario A**

Assume a min GPU utilization target of 80%. Suppose that at `t = 0`, current size is 120, and 80 nodes are utilized.
* In the evaluate stage, observe that current utilization is less than 80%. Set `targetSize` to 100.
* In the reconcile stage, taint 20 nodes with the deletion timestamp.
* At the end of reconciliation, current size remains 120 and target size remains 100.

Suppose there are no changes in utilization over the next `scaleDownDelay` seconds. At `t = scaleDownDelay`:
* In the evaluate stage, there are no changes to the desired state.
* In the reconcile stage, deprovision the 20 nodes previously tainted for deletion.

**Scenario B**

Assume the same starting state as scenario A. Suppose that at `t = scaleDownDelay`, the number of utilized nodes drops to 60.
* In the evaluate stage, set `targetSize` to 75 (previously 100).
* In the reconcile stage, deprovision the 20 nodes previously tainted for deletion.

In the next iteration, taint an additional 25 nodes for deletion.

Assuming no changes in utilization, at `t = 2 * scaleDownDelay`:
* In the evaluate stage, there are no changes to the desired state.
* In the reconcile stage, deprovision the 25 nodes previously tainted for deletion.

**Scenario C**

Again, assume the same starting state as scenario A. Suppose at some `0 < t < scaleDownDelay`, the number of utilized nodes increases to 88.
* In the evaluate stage, set `targetSize` to 110 (previously 100).
* In the reconcile stage, remove taints from 10 nodes to meet the target number of nodes scheduled for deletion.

At `t = scaleDownDelay`, deprovision the 10 nodes scheduled for deletion.

## Cloud provider logic
The reconciler interacts with cloud providers using the `CloudProvider` interface.
